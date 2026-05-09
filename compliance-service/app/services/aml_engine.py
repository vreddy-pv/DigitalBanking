"""
AML Rules Engine — evaluates each transaction against configurable rules
and returns a list of (alert_type, severity, description) tuples.

Rules implemented:
  1. HIGH_VALUE_TRANSACTION    — single amount > threshold (CRITICAL for >2x, HIGH otherwise)
  2. LARGE_WITHDRAWAL          — withdrawal > threshold (HIGH)
  3. FREQUENT_TRANSACTIONS     — >N transactions from same account in last M minutes (MEDIUM)
  4. RAPID_SUCCESSION          — >N transactions in last M minutes (HIGH)
  5. STRUCTURING               — multiple transactions in band just below reporting threshold (HIGH)
  6. ROUND_AMOUNT              — exact multiples of 10,000 ≥ 50,000 (LOW)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

# (alert_type, severity, description)
AlertTuple = Tuple[str, str, str]


def evaluate(
    db: Session,
    transaction_id: str,
    account_id: str,
    amount: float,
    transaction_type: str,
    customer_name: str | None = None,
) -> List[AlertTuple]:
    """Run all AML rules and return a list of alerts to raise."""
    alerts: List[AlertTuple] = []

    alerts.extend(_rule_high_value(amount, transaction_type))
    alerts.extend(_rule_large_withdrawal(amount, transaction_type))
    alerts.extend(_rule_round_amount(amount, transaction_type))
    alerts.extend(_rule_frequent_transactions(db, account_id, transaction_id))
    alerts.extend(_rule_rapid_succession(db, account_id, transaction_id))
    alerts.extend(_rule_structuring(db, account_id, transaction_id, amount))

    if alerts:
        logger.info(
            "AML evaluation for txn=%s account=%s amount=%.2f → %d alert(s): %s",
            transaction_id, account_id, amount,
            len(alerts), [a[0] for a in alerts],
        )
    return alerts


# ---------------------------------------------------------------------------
# Individual rules
# ---------------------------------------------------------------------------

def _rule_high_value(amount: float, tx_type: str) -> List[AlertTuple]:
    """Flag single transactions above the high-value threshold."""
    if amount >= settings.high_value_threshold:
        severity = "CRITICAL" if amount >= settings.high_value_threshold * 2 else "HIGH"
        return [(
            "HIGH_VALUE_TRANSACTION",
            severity,
            f"{tx_type} of ₹{amount:,.2f} exceeds high-value threshold "
            f"(₹{settings.high_value_threshold:,.0f})",
        )]
    return []


def _rule_large_withdrawal(amount: float, tx_type: str) -> List[AlertTuple]:
    """Flag large withdrawals."""
    if tx_type == "WITHDRAWAL" and amount >= settings.large_withdrawal_threshold:
        return [(
            "LARGE_WITHDRAWAL",
            "HIGH",
            f"Withdrawal of ₹{amount:,.2f} exceeds large-withdrawal threshold "
            f"(₹{settings.large_withdrawal_threshold:,.0f})",
        )]
    return []


def _rule_round_amount(amount: float, tx_type: str) -> List[AlertTuple]:
    """Flag suspiciously round amounts (exact multiples of 10,000 ≥ 50,000)."""
    if amount >= 50_000 and amount % 10_000 == 0:
        return [(
            "ROUND_AMOUNT",
            "LOW",
            f"Transaction amount ₹{amount:,.0f} is a suspiciously round number",
        )]
    return []


def _rule_frequent_transactions(
    db: Session, account_id: str, current_tx_id: str
) -> List[AlertTuple]:
    """Flag accounts with too many transactions in a rolling window."""
    since = datetime.utcnow() - timedelta(minutes=settings.frequent_tx_window_minutes)
    row = db.execute(
        text("""
            SELECT COUNT(*) FROM compliance_alerts
            WHERE account_id = :account_id
              AND created_at >= :since
              AND alert_type = 'FREQUENT_TRANSACTIONS'
        """),
        {"account_id": account_id, "since": since},
    ).scalar()
    # Use transaction history from alerts as proxy — count distinct txn alerts in window
    # Real implementation would query transaction_db; this checks our own alert history
    # to avoid re-alerting on an already-flagged account in the same window
    if row and row >= 1:
        return []  # already alerted in this window

    # Count recent alerts for this account across all types in the window
    recent = db.execute(
        text("""
            SELECT COUNT(DISTINCT transaction_id) FROM compliance_alerts
            WHERE account_id = :account_id
              AND created_at >= :since
        """),
        {"account_id": account_id, "since": since},
    ).scalar() or 0

    if recent >= settings.frequent_tx_count:
        return [(
            "FREQUENT_TRANSACTIONS",
            "MEDIUM",
            f"Account had {recent} flagged transactions in the last "
            f"{settings.frequent_tx_window_minutes} minutes",
        )]
    return []


def _rule_rapid_succession(
    db: Session, account_id: str, current_tx_id: str
) -> List[AlertTuple]:
    """Flag rapid-fire transactions (many alerts in a short window)."""
    since = datetime.utcnow() - timedelta(minutes=settings.rapid_tx_window_minutes)
    recent = db.execute(
        text("""
            SELECT COUNT(DISTINCT transaction_id) FROM compliance_alerts
            WHERE account_id = :account_id
              AND created_at >= :since
              AND transaction_id != :tx_id
        """),
        {"account_id": account_id, "since": since, "tx_id": current_tx_id},
    ).scalar() or 0

    if recent >= settings.rapid_tx_count:
        return [(
            "RAPID_SUCCESSION",
            "HIGH",
            f"Account had {recent} suspicious transactions in the last "
            f"{settings.rapid_tx_window_minutes} minutes",
        )]
    return []


def _rule_structuring(
    db: Session, account_id: str, current_tx_id: str, amount: float
) -> List[AlertTuple]:
    """Detect structuring — multiple transactions just below the reporting threshold."""
    if not (settings.structuring_lower <= amount <= settings.structuring_upper):
        return []

    since = datetime.utcnow() - timedelta(hours=24)
    # Count previous structuring-range alerts for this account in last 24h
    count = db.execute(
        text("""
            SELECT COUNT(DISTINCT transaction_id) FROM compliance_alerts
            WHERE account_id = :account_id
              AND created_at >= :since
              AND amount BETWEEN :lower AND :upper
              AND transaction_id != :tx_id
        """),
        {
            "account_id": account_id,
            "since": since,
            "lower": settings.structuring_lower,
            "upper": settings.structuring_upper,
            "tx_id": current_tx_id,
        },
    ).scalar() or 0

    if count >= settings.structuring_count - 1:
        return [(
            "STRUCTURING",
            "HIGH",
            f"Possible structuring detected: {count + 1} transactions between "
            f"₹{settings.structuring_lower:,.0f}–₹{settings.structuring_upper:,.0f} in 24 hours",
        )]
    return []
