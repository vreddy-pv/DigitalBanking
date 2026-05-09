"""
Customer Risk Scoring — derives a 0-100 risk score from alert history.

Score components:
  CRITICAL alert: +30 pts  (capped at 3)
  HIGH alert:     +20 pts  (capped at 3)
  MEDIUM alert:   +10 pts  (capped at 5)
  LOW alert:       +3 pts  (capped at 10)

Risk levels:
  0-20   → LOW
  21-50  → MEDIUM
  51-80  → HIGH
  81-100 → CRITICAL
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

_SEVERITY_POINTS = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10, "LOW": 3}
_SEVERITY_CAPS = {"CRITICAL": 3, "HIGH": 3, "MEDIUM": 5, "LOW": 10}


def compute_risk_score(db: Session, account_id: str) -> tuple[int, str]:
    """Compute risk score for an account based on all-time alert history."""
    rows = db.execute(
        text("""
            SELECT severity, COUNT(*) as cnt
            FROM compliance_alerts
            WHERE account_id = :account_id
            GROUP BY severity
        """),
        {"account_id": account_id},
    ).fetchall()

    score = 0
    for row in rows:
        severity = row[0]
        count = row[1]
        pts = _SEVERITY_POINTS.get(severity, 0)
        cap = _SEVERITY_CAPS.get(severity, 0)
        score += pts * min(count, cap)

    score = min(score, 100)
    level = _score_to_level(score)
    return score, level


def _score_to_level(score: int) -> str:
    if score <= 20:
        return "LOW"
    elif score <= 50:
        return "MEDIUM"
    elif score <= 80:
        return "HIGH"
    return "CRITICAL"
