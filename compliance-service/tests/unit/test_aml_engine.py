"""Unit tests for the AML rules engine."""
import pytest
from unittest.mock import MagicMock, patch
from app.services import aml_engine
from app.config import settings


def _make_db(recent_alerts=0, recent_structuring=0):
    """Create a mock DB session that returns configurable counts."""
    db = MagicMock()
    # scalar() returns for frequent/rapid/structuring queries
    scalar_side_effects = [0, recent_alerts, recent_structuring]
    db.execute.return_value.scalar.side_effect = scalar_side_effects
    db.execute.return_value.fetchall.return_value = []
    return db


class TestHighValueRule:
    def test_no_alert_below_threshold(self):
        db = _make_db()
        alerts = aml_engine._rule_high_value(10_000, "DEPOSIT")
        assert alerts == []

    def test_high_alert_at_threshold(self):
        db = _make_db()
        alerts = aml_engine._rule_high_value(settings.high_value_threshold, "DEPOSIT")
        assert len(alerts) == 1
        assert alerts[0][0] == "HIGH_VALUE_TRANSACTION"
        assert alerts[0][1] == "HIGH"

    def test_critical_alert_at_double_threshold(self):
        alerts = aml_engine._rule_high_value(settings.high_value_threshold * 2, "TRANSFER")
        assert len(alerts) == 1
        assert alerts[0][1] == "CRITICAL"

    def test_withdrawal_also_flagged(self):
        alerts = aml_engine._rule_high_value(60_000, "WITHDRAWAL")
        assert len(alerts) == 1


class TestLargeWithdrawalRule:
    def test_no_alert_on_deposit(self):
        alerts = aml_engine._rule_large_withdrawal(30_000, "DEPOSIT")
        assert alerts == []

    def test_alert_on_large_withdrawal(self):
        alerts = aml_engine._rule_large_withdrawal(settings.large_withdrawal_threshold, "WITHDRAWAL")
        assert len(alerts) == 1
        assert alerts[0][0] == "LARGE_WITHDRAWAL"
        assert alerts[0][1] == "HIGH"

    def test_no_alert_below_threshold(self):
        alerts = aml_engine._rule_large_withdrawal(10_000, "WITHDRAWAL")
        assert alerts == []


class TestRoundAmountRule:
    def test_alert_on_exact_50000(self):
        alerts = aml_engine._rule_round_amount(50_000, "DEPOSIT")
        assert len(alerts) == 1
        assert alerts[0][0] == "ROUND_AMOUNT"
        assert alerts[0][1] == "LOW"

    def test_no_alert_on_non_round(self):
        alerts = aml_engine._rule_round_amount(50_001, "DEPOSIT")
        assert alerts == []

    def test_no_alert_below_50000(self):
        alerts = aml_engine._rule_round_amount(10_000, "WITHDRAWAL")
        assert alerts == []

    def test_alert_on_large_round(self):
        alerts = aml_engine._rule_round_amount(100_000, "TRANSFER")
        assert len(alerts) == 1


class TestStructuringRule:
    def test_no_alert_outside_range(self):
        db = _make_db()
        alerts = aml_engine._rule_structuring(db, "acc-1", "tx-1", 10_000)
        assert alerts == []

    def test_alert_with_enough_history(self):
        db = MagicMock()
        db.execute.return_value.scalar.return_value = settings.structuring_count - 1
        alerts = aml_engine._rule_structuring(db, "acc-1", "tx-1", settings.structuring_lower + 1000)
        assert len(alerts) == 1
        assert alerts[0][0] == "STRUCTURING"
        assert alerts[0][1] == "HIGH"


class TestRiskScoring:
    def test_zero_score_no_alerts(self):
        from app.services.risk_scoring import compute_risk_score, _score_to_level
        db = MagicMock()
        db.execute.return_value.fetchall.return_value = []
        score, level = compute_risk_score(db, "acc-1")
        assert score == 0
        assert level == "LOW"

    def test_score_levels(self):
        from app.services.risk_scoring import _score_to_level
        assert _score_to_level(0) == "LOW"
        assert _score_to_level(20) == "LOW"
        assert _score_to_level(21) == "MEDIUM"
        assert _score_to_level(50) == "MEDIUM"
        assert _score_to_level(51) == "HIGH"
        assert _score_to_level(80) == "HIGH"
        assert _score_to_level(81) == "CRITICAL"
        assert _score_to_level(100) == "CRITICAL"

    def test_score_capped_at_100(self):
        from app.services.risk_scoring import compute_risk_score
        db = MagicMock()
        # 10 CRITICAL alerts × 30 pts each = 300, capped at 100
        db.execute.return_value.fetchall.return_value = [("CRITICAL", 10)]
        score, level = compute_risk_score(db, "acc-1")
        assert score == 100
        assert level == "CRITICAL"
