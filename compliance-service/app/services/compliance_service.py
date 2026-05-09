import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.compliance_alert import ComplianceAlert, CustomerRiskProfile
from app.schemas.compliance_schema import (
    AmlCheckResult,
    AlertListResponse,
    AlertResponse,
    ReviewRequest,
    RiskProfileResponse,
    ComplianceStats,
    ManualCheckRequest,
    TransactionCreatedEvent,
)
from app.services import aml_engine, risk_scoring

logger = logging.getLogger(__name__)


def process_transaction_event(db: Session, event: TransactionCreatedEvent) -> AmlCheckResult:
    """Main entry point — run AML checks on an incoming transaction event."""
    account_id = event.to_account_id or event.from_account_id or "unknown"

    alerts = aml_engine.evaluate(
        db=db,
        transaction_id=event.transaction_id,
        account_id=account_id,
        amount=event.amount,
        transaction_type=event.transaction_type,
        customer_name=event.customer_name,
    )

    alert_types = []
    highest_severity = "NONE"
    severity_rank = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    for alert_type, severity, description in alerts:
        alert = ComplianceAlert(
            transaction_id=event.transaction_id,
            account_id=account_id,
            customer_name=event.customer_name,
            amount=event.amount,
            transaction_type=event.transaction_type,
            alert_type=alert_type,
            severity=severity,
            description=description,
            status="PENDING",
        )
        db.add(alert)
        alert_types.append(alert_type)
        if severity_rank.get(severity, 0) > severity_rank.get(highest_severity, 0):
            highest_severity = severity

    if alerts:
        db.commit()
        _update_risk_profile(db, account_id, len(alerts))

    return AmlCheckResult(
        transaction_id=event.transaction_id,
        alerts_raised=len(alerts),
        alert_types=alert_types,
        highest_severity=highest_severity,
    )


def manual_check(db: Session, req: ManualCheckRequest) -> AmlCheckResult:
    """Manually trigger AML check (used by admin or other services)."""
    fake_event = TransactionCreatedEvent(
        transaction_id=req.transaction_id,
        transaction_type=req.transaction_type,
        amount=req.amount,
        to_account_id=req.account_id if req.transaction_type in ("DEPOSIT", "TRANSFER") else None,
        from_account_id=req.account_id if req.transaction_type in ("WITHDRAWAL", "TRANSFER") else None,
        customer_name=req.customer_name,
    )
    return process_transaction_event(db, fake_event)


def get_alerts(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    account_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> AlertListResponse:
    query = db.query(ComplianceAlert)
    if status:
        query = query.filter(ComplianceAlert.status == status)
    if severity:
        query = query.filter(ComplianceAlert.severity == severity)
    if account_id:
        query = query.filter(ComplianceAlert.account_id == account_id)

    total = query.count()
    alerts = query.order_by(ComplianceAlert.created_at.desc()).offset(offset).limit(limit).all()

    return AlertListResponse(
        total=total,
        alerts=[AlertResponse.model_validate(a) for a in alerts],
    )


def get_alert(db: Session, alert_id: str) -> Optional[AlertResponse]:
    alert = db.query(ComplianceAlert).filter(ComplianceAlert.id == alert_id).first()
    if not alert:
        return None
    return AlertResponse.model_validate(alert)


def review_alert(db: Session, alert_id: str, req: ReviewRequest) -> Optional[AlertResponse]:
    alert = db.query(ComplianceAlert).filter(ComplianceAlert.id == alert_id).first()
    if not alert:
        return None
    alert.status = req.status
    alert.reviewed_by = req.reviewed_by
    alert.reviewed_at = datetime.utcnow()
    alert.review_notes = req.review_notes
    db.commit()
    db.refresh(alert)
    return AlertResponse.model_validate(alert)


def get_customer_risk(db: Session, account_id: str) -> RiskProfileResponse:
    profile = db.query(CustomerRiskProfile).filter(
        CustomerRiskProfile.customer_id == account_id
    ).first()
    if not profile:
        # Return default LOW risk if no profile exists
        return RiskProfileResponse(
            customer_id=account_id,
            risk_score=0,
            risk_level="LOW",
            alert_count=0,
            high_alert_count=0,
            last_assessed_at=datetime.utcnow(),
        )
    return RiskProfileResponse.model_validate(profile)


def get_stats(db: Session) -> ComplianceStats:
    total = db.query(ComplianceAlert).count()
    pending = db.query(ComplianceAlert).filter(ComplianceAlert.status == "PENDING").count()
    cleared = db.query(ComplianceAlert).filter(ComplianceAlert.status == "CLEARED").count()
    escalated = db.query(ComplianceAlert).filter(ComplianceAlert.status == "ESCALATED").count()
    high_risk = db.query(CustomerRiskProfile).filter(
        CustomerRiskProfile.risk_level.in_(["HIGH", "CRITICAL"])
    ).count()

    by_severity = dict(db.execute(
        text("SELECT severity, COUNT(*) FROM compliance_alerts GROUP BY severity")
    ).fetchall())
    by_type = dict(db.execute(
        text("SELECT alert_type, COUNT(*) FROM compliance_alerts GROUP BY alert_type")
    ).fetchall())

    return ComplianceStats(
        total_alerts=total,
        pending_alerts=pending,
        cleared_alerts=cleared,
        escalated_alerts=escalated,
        high_risk_customers=high_risk,
        alerts_by_severity=by_severity,
        alerts_by_type=by_type,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _update_risk_profile(db: Session, account_id: str, new_alerts: int) -> None:
    """Recompute and persist the customer risk profile."""
    score, level = risk_scoring.compute_risk_score(db, account_id)

    profile = db.query(CustomerRiskProfile).filter(
        CustomerRiskProfile.customer_id == account_id
    ).first()

    total_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.account_id == account_id
    ).count()
    high_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.account_id == account_id,
        ComplianceAlert.severity.in_(["HIGH", "CRITICAL"]),
    ).count()

    if profile:
        profile.risk_score = score
        profile.risk_level = level
        profile.alert_count = total_alerts
        profile.high_alert_count = high_alerts
        profile.last_assessed_at = datetime.utcnow()
    else:
        profile = CustomerRiskProfile(
            customer_id=account_id,
            risk_score=score,
            risk_level=level,
            alert_count=total_alerts,
            high_alert_count=high_alerts,
            last_assessed_at=datetime.utcnow(),
        )
        db.add(profile)

    db.commit()
    logger.info("Risk profile updated: account=%s score=%d level=%s", account_id, score, level)
