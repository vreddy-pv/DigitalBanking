from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from app.database import get_db
from app.schemas.compliance_schema import (
    AlertListResponse,
    AlertResponse,
    ReviewRequest,
    RiskProfileResponse,
    ComplianceStats,
    ManualCheckRequest,
    AmlCheckResult,
)
from app.services import compliance_service

compliance_router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])

ALERTS_RAISED = Counter("compliance_alerts_total", "Total compliance alerts raised", ["severity", "alert_type"])
CHECKS_TOTAL = Counter("compliance_checks_total", "Total AML checks performed")


# ------------------------------------------------------------------
# Metrics endpoint (for Prometheus scraping)
# ------------------------------------------------------------------

@compliance_router.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ------------------------------------------------------------------
# Stats — must come BEFORE /{alert_id} to avoid path collision
# ------------------------------------------------------------------

@compliance_router.get("/stats", response_model=ComplianceStats)
def get_stats(db: Session = Depends(get_db)):
    """Platform-wide compliance statistics."""
    return compliance_service.get_stats(db)


# ------------------------------------------------------------------
# Manual AML check
# ------------------------------------------------------------------

@compliance_router.post("/check", response_model=AmlCheckResult, status_code=201)
def manual_check(req: ManualCheckRequest, db: Session = Depends(get_db)):
    """Manually trigger an AML check for a transaction (admin/testing use)."""
    CHECKS_TOTAL.inc()
    result = compliance_service.manual_check(db, req)
    for atype in result.alert_types:
        ALERTS_RAISED.labels(severity=result.highest_severity, alert_type=atype).inc()
    return result


# ------------------------------------------------------------------
# Alert CRUD
# ------------------------------------------------------------------

@compliance_router.get("/alerts", response_model=AlertListResponse)
def list_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    account_id: Optional[str] = Query(None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List compliance alerts with optional filters."""
    return compliance_service.get_alerts(db, status, severity, account_id, limit, offset)


@compliance_router.get("/alerts/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = compliance_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@compliance_router.put("/alerts/{alert_id}/review", response_model=AlertResponse)
def review_alert(alert_id: str, req: ReviewRequest, db: Session = Depends(get_db)):
    """Review a compliance alert — mark as REVIEWED, CLEARED, or ESCALATED."""
    alert = compliance_service.review_alert(db, alert_id, req)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# ------------------------------------------------------------------
# Customer risk profile
# ------------------------------------------------------------------

@compliance_router.get("/customers/{account_id}/risk", response_model=RiskProfileResponse)
def get_customer_risk(account_id: str, db: Session = Depends(get_db)):
    """Get the AML risk profile for a customer account."""
    return compliance_service.get_customer_risk(db, account_id)
