"""Unit tests for ledger_analytics service. DB connection is fully mocked."""
import uuid
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock

from app.services import ledger_analytics


def _make_row(mapping: dict):
    """Create a mock row whose ._mapping attribute returns a dict-like object."""
    row = MagicMock()
    row._mapping = mapping
    return row


TXN_ID = str(uuid.uuid4())
GL_ID = str(uuid.uuid4())
JOURNAL_ID = str(uuid.uuid4())
NOW = datetime(2026, 5, 9, 10, 0, 0)


class TestTrialBalance:
    def test_trial_balance_aggregates_debits_credits(self):
        conn = MagicMock()
        rows = [
            _make_row(
                {
                    "account_code": "1001",
                    "account_name": "Cash",
                    "account_type": "ASSET",
                    "total_debits": Decimal("5000.00"),
                    "total_credits": Decimal("2000.00"),
                    "balance": Decimal("3000.00"),
                }
            ),
            _make_row(
                {
                    "account_code": "2001",
                    "account_name": "Accounts Payable",
                    "account_type": "LIABILITY",
                    "total_debits": Decimal("1000.00"),
                    "total_credits": Decimal("3500.00"),
                    "balance": Decimal("-2500.00"),
                }
            ),
        ]
        conn.execute.return_value.fetchall.return_value = rows

        result = ledger_analytics.get_trial_balance(conn)

        assert len(result) == 2

        cash = result[0]
        assert cash["account_code"] == "1001"
        assert cash["account_name"] == "Cash"
        assert cash["account_type"] == "ASSET"
        assert cash["total_debits"] == Decimal("5000.00")
        assert cash["total_credits"] == Decimal("2000.00")
        assert cash["balance"] == Decimal("3000.00")

        ap = result[1]
        assert ap["account_code"] == "2001"
        assert ap["total_credits"] == Decimal("3500.00")
        assert ap["balance"] == Decimal("-2500.00")

    def test_trial_balance_empty(self):
        conn = MagicMock()
        conn.execute.return_value.fetchall.return_value = []
        result = ledger_analytics.get_trial_balance(conn)
        assert result == []


class TestJournalEntries:
    def test_journal_entries_for_transaction(self):
        conn = MagicMock()
        gl_id_1 = uuid.uuid4()
        gl_id_2 = uuid.uuid4()
        je_id_1 = uuid.uuid4()
        je_id_2 = uuid.uuid4()

        rows = [
            _make_row(
                {
                    "id": je_id_1,
                    "gl_account_id": gl_id_1,
                    "gl_account_code": "1001",
                    "gl_account_name": "Cash",
                    "debit": Decimal("500.00"),
                    "credit": Decimal("0.00"),
                    "timestamp": NOW,
                }
            ),
            _make_row(
                {
                    "id": je_id_2,
                    "gl_account_id": gl_id_2,
                    "gl_account_code": "4001",
                    "gl_account_name": "Revenue",
                    "debit": Decimal("0.00"),
                    "credit": Decimal("500.00"),
                    "timestamp": NOW,
                }
            ),
        ]
        conn.execute.return_value.fetchall.return_value = rows

        result = ledger_analytics.get_journal_entries_for_transaction(conn, TXN_ID)

        assert len(result) == 2

        debit_entry = result[0]
        assert debit_entry["gl_account_code"] == "1001"
        assert debit_entry["gl_account_name"] == "Cash"
        assert debit_entry["debit"] == Decimal("500.00")
        assert debit_entry["credit"] == Decimal("0.00")
        assert debit_entry["timestamp"] == NOW

        credit_entry = result[1]
        assert credit_entry["gl_account_code"] == "4001"
        assert credit_entry["debit"] == Decimal("0.00")
        assert credit_entry["credit"] == Decimal("500.00")

    def test_journal_entries_no_match(self):
        conn = MagicMock()
        conn.execute.return_value.fetchall.return_value = []
        result = ledger_analytics.get_journal_entries_for_transaction(conn, TXN_ID)
        assert result == []
