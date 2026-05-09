"""Unit tests for transaction_analytics service. DB connection is fully mocked."""
import uuid
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

from app.services import transaction_analytics


def _make_row(mapping: dict):
    """Create a mock row whose ._mapping attribute returns a dict-like object."""
    row = MagicMock()
    row._mapping = mapping
    return row


ACCOUNT_ID = str(uuid.uuid4())
OTHER_ACCOUNT = str(uuid.uuid4())
TXN_ID = str(uuid.uuid4())
NOW = datetime(2026, 5, 9, 12, 0, 0)


class TestGetStatement:
    def test_get_statement_returns_paginated_rows(self):
        conn = MagicMock()

        count_row = _make_row({"total": 2})
        txn_row_credit = _make_row(
            {
                "id": uuid.UUID(TXN_ID),
                "type": "DEPOSIT",
                "amount": Decimal("500.00"),
                "status": "COMPLETED",
                "description": "Salary",
                "created_at": NOW,
                "from_account_id": uuid.UUID(OTHER_ACCOUNT),
                "to_account_id": uuid.UUID(ACCOUNT_ID),
            }
        )
        txn_row_debit = _make_row(
            {
                "id": uuid.UUID(TXN_ID),
                "type": "WITHDRAWAL",
                "amount": Decimal("100.00"),
                "status": "COMPLETED",
                "description": "ATM",
                "created_at": NOW,
                "from_account_id": uuid.UUID(ACCOUNT_ID),
                "to_account_id": uuid.UUID(OTHER_ACCOUNT),
            }
        )

        conn.execute.side_effect = [
            MagicMock(fetchone=MagicMock(return_value=count_row)),
            MagicMock(fetchall=MagicMock(return_value=[txn_row_credit, txn_row_debit])),
        ]

        result = transaction_analytics.get_statement(conn, ACCOUNT_ID, page=1, page_size=20)

        assert result["total"] == 2
        assert result["page"] == 1
        assert result["page_size"] == 20
        assert len(result["items"]) == 2
        assert result["items"][0]["direction"] == "CREDIT"
        assert result["items"][1]["direction"] == "DEBIT"

    def test_get_statement_empty_account(self):
        conn = MagicMock()
        count_row = _make_row({"total": 0})
        conn.execute.side_effect = [
            MagicMock(fetchone=MagicMock(return_value=count_row)),
            MagicMock(fetchall=MagicMock(return_value=[])),
        ]
        result = transaction_analytics.get_statement(conn, ACCOUNT_ID)
        assert result["total"] == 0
        assert result["items"] == []


class TestGetSummary:
    def test_get_summary_calculates_credits_debits(self):
        conn = MagicMock()
        summary_row = _make_row(
            {
                "total_credits": Decimal("1000.00"),
                "total_debits": Decimal("300.00"),
                "transaction_count": 5,
            }
        )
        conn.execute.return_value.fetchone.return_value = summary_row

        result = transaction_analytics.get_summary(conn, ACCOUNT_ID, month="2026-05")

        assert result["total_credits"] == Decimal("1000.00")
        assert result["total_debits"] == Decimal("300.00")
        assert result["net"] == Decimal("700.00")
        assert result["transaction_count"] == 5
        assert result["month"] == "2026-05"

    def test_get_summary_defaults_to_current_month(self):
        conn = MagicMock()
        summary_row = _make_row(
            {"total_credits": Decimal("0"), "total_debits": Decimal("0"), "transaction_count": 0}
        )
        conn.execute.return_value.fetchone.return_value = summary_row

        result = transaction_analytics.get_summary(conn, ACCOUNT_ID, month=None)

        now = datetime.utcnow()
        expected_month = now.strftime("%Y-%m")
        assert result["month"] == expected_month


class TestGetSpendingBreakdown:
    def test_get_spending_breakdown_by_type(self):
        conn = MagicMock()
        rows = [
            _make_row({"type": "WITHDRAWAL", "total_amount": Decimal("300.00"), "transaction_count": 3}),
            _make_row({"type": "TRANSFER", "total_amount": Decimal("200.00"), "transaction_count": 2}),
        ]
        conn.execute.return_value.fetchall.return_value = rows

        result = transaction_analytics.get_spending_breakdown(conn, ACCOUNT_ID)

        assert len(result) == 2
        assert result[0]["type"] == "WITHDRAWAL"
        assert result[0]["transaction_count"] == 3
        assert result[0]["percentage"] == pytest.approx(60.0, abs=0.01)
        assert result[1]["type"] == "TRANSFER"
        assert result[1]["percentage"] == pytest.approx(40.0, abs=0.01)

    def test_get_spending_breakdown_empty(self):
        conn = MagicMock()
        conn.execute.return_value.fetchall.return_value = []
        result = transaction_analytics.get_spending_breakdown(conn, ACCOUNT_ID)
        assert result == []


class TestPlatformSummary:
    def test_platform_summary_counts(self):
        conn = MagicMock()
        summary_row = _make_row(
            {
                "total_transactions": 100,
                "total_volume": Decimal("50000.00"),
                "avg_transaction_amount": Decimal("500.00"),
                "completed_transactions": 80,
                "pending_transactions": 15,
                "failed_transactions": 5,
            }
        )
        conn.execute.return_value.fetchone.return_value = summary_row

        result = transaction_analytics.get_platform_summary(conn)

        assert result["total_transactions"] == 100
        assert result["total_volume"] == Decimal("50000.00")
        assert result["completed_transactions"] == 80
        assert result["pending_transactions"] == 15
        assert result["failed_transactions"] == 5
        assert result["avg_transaction_amount"] == Decimal("500.00")

    def test_platform_summary_no_data(self):
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        result = transaction_analytics.get_platform_summary(conn)
        assert result["total_transactions"] == 0
        assert result["total_volume"] == Decimal("0")
