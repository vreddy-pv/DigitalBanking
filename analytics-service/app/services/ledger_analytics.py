from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import List, Dict, Any
from decimal import Decimal


def get_trial_balance(conn: Connection) -> List[Dict[str, Any]]:
    """Return all GL accounts with aggregated debit/credit totals from journal entries."""
    sql = text(
        """
        SELECT
            ga.code AS account_code,
            ga.name AS account_name,
            ga.type AS account_type,
            COALESCE(SUM(je.debit), 0) AS total_debits,
            COALESCE(SUM(je.credit), 0) AS total_credits,
            COALESCE(SUM(je.debit), 0) - COALESCE(SUM(je.credit), 0) AS balance
        FROM gl_accounts ga
        LEFT JOIN journal_entries je ON ga.id = je.gl_account_id
        GROUP BY ga.id, ga.code, ga.name, ga.type
        ORDER BY ga.code
        """
    )
    rows = conn.execute(sql).fetchall()

    result = []
    for row in rows:
        m = row._mapping
        result.append(
            {
                "account_code": m["account_code"],
                "account_name": m["account_name"],
                "account_type": m["account_type"],
                "total_debits": Decimal(str(m["total_debits"])),
                "total_credits": Decimal(str(m["total_credits"])),
                "balance": Decimal(str(m["balance"])),
            }
        )

    return result


def get_journal_entries_for_transaction(
    conn: Connection,
    transaction_id: str,
) -> List[Dict[str, Any]]:
    """Return journal entries for a specific transaction, joined with GL account details."""
    sql = text(
        """
        SELECT
            je.id,
            je.gl_account_id,
            ga.code AS gl_account_code,
            ga.name AS gl_account_name,
            je.debit,
            je.credit,
            je.timestamp
        FROM journal_entries je
        JOIN gl_accounts ga ON je.gl_account_id = ga.id
        WHERE je.transaction_id = :transaction_id
        ORDER BY je.timestamp
        """
    )
    rows = conn.execute(sql, {"transaction_id": transaction_id}).fetchall()

    result = []
    for row in rows:
        m = row._mapping
        result.append(
            {
                "id": m["id"],
                "gl_account_id": m["gl_account_id"],
                "gl_account_code": m["gl_account_code"],
                "gl_account_name": m["gl_account_name"],
                "debit": Decimal(str(m["debit"])),
                "credit": Decimal(str(m["credit"])),
                "timestamp": m["timestamp"],
            }
        )

    return result
