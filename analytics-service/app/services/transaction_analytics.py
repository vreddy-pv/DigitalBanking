from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import calendar


def get_statement(
    conn: Connection,
    account_id: str,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """Return paginated transaction history for an account (FROM or TO), ordered by created_at DESC."""
    offset = (page - 1) * page_size

    count_sql = text(
        """
        SELECT COUNT(*) AS total
        FROM transactions
        WHERE from_account_id = :account_id OR to_account_id = :account_id
        """
    )
    total_row = conn.execute(count_sql, {"account_id": account_id}).fetchone()
    total = total_row._mapping["total"] if total_row else 0

    rows_sql = text(
        """
        SELECT
            id,
            type,
            amount,
            status,
            description,
            created_at,
            from_account_id,
            to_account_id
        FROM transactions
        WHERE from_account_id = :account_id OR to_account_id = :account_id
        ORDER BY created_at DESC
        LIMIT :page_size OFFSET :offset
        """
    )
    rows = conn.execute(
        rows_sql,
        {"account_id": account_id, "page_size": page_size, "offset": offset},
    ).fetchall()

    items = []
    for row in rows:
        m = row._mapping
        # Determine direction from the perspective of account_id
        if str(m["to_account_id"]) == str(account_id):
            direction = "CREDIT"
        else:
            direction = "DEBIT"

        items.append(
            {
                "id": m["id"],
                "type": m["type"],
                "amount": m["amount"],
                "status": m["status"],
                "description": m["description"],
                "created_at": m["created_at"],
                "direction": direction,
            }
        )

    return {
        "account_id": account_id,
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items,
    }


def get_summary(
    conn: Connection,
    account_id: str,
    month: Optional[str] = None,
) -> Dict[str, Any]:
    """Return monthly credit/debit summary for an account. Month format: YYYY-MM."""
    if month is None:
        now = datetime.utcnow()
        month = now.strftime("%Y-%m")

    try:
        year, mon = int(month.split("-")[0]), int(month.split("-")[1])
    except (ValueError, IndexError):
        now = datetime.utcnow()
        year, mon = now.year, now.month

    last_day = calendar.monthrange(year, mon)[1]
    month_start = f"{year}-{mon:02d}-01 00:00:00"
    month_end = f"{year}-{mon:02d}-{last_day} 23:59:59"

    sql = text(
        """
        SELECT
            COALESCE(SUM(CASE WHEN to_account_id = :account_id THEN amount ELSE 0 END), 0) AS total_credits,
            COALESCE(SUM(CASE WHEN from_account_id = :account_id THEN amount ELSE 0 END), 0) AS total_debits,
            COUNT(*) AS transaction_count
        FROM transactions
        WHERE (from_account_id = :account_id OR to_account_id = :account_id)
          AND created_at >= :month_start
          AND created_at <= :month_end
        """
    )
    row = conn.execute(
        sql,
        {
            "account_id": account_id,
            "month_start": month_start,
            "month_end": month_end,
        },
    ).fetchone()

    total_credits = Decimal(str(row._mapping["total_credits"])) if row else Decimal("0")
    total_debits = Decimal(str(row._mapping["total_debits"])) if row else Decimal("0")
    transaction_count = row._mapping["transaction_count"] if row else 0

    return {
        "account_id": account_id,
        "month": month,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net": total_credits - total_debits,
        "transaction_count": transaction_count,
    }


def get_spending_breakdown(
    conn: Connection,
    account_id: str,
) -> List[Dict[str, Any]]:
    """Return spending breakdown by transaction type for an account."""
    sql = text(
        """
        SELECT
            type,
            COALESCE(SUM(amount), 0) AS total_amount,
            COUNT(*) AS transaction_count
        FROM transactions
        WHERE from_account_id = :account_id OR to_account_id = :account_id
        GROUP BY type
        ORDER BY total_amount DESC
        """
    )
    rows = conn.execute(sql, {"account_id": account_id}).fetchall()

    if not rows:
        return []

    grand_total = sum(Decimal(str(r._mapping["total_amount"])) for r in rows)

    result = []
    for row in rows:
        m = row._mapping
        total_amount = Decimal(str(m["total_amount"]))
        percentage = float((total_amount / grand_total * 100).quantize(Decimal("0.01"))) if grand_total else 0.0
        result.append(
            {
                "type": m["type"],
                "total_amount": total_amount,
                "transaction_count": m["transaction_count"],
                "percentage": percentage,
            }
        )

    return result


def get_platform_summary(conn: Connection) -> Dict[str, Any]:
    """Return platform-wide transaction statistics."""
    sql = text(
        """
        SELECT
            COUNT(*) AS total_transactions,
            COALESCE(SUM(amount), 0) AS total_volume,
            COALESCE(AVG(amount), 0) AS avg_transaction_amount,
            COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed_transactions,
            COUNT(*) FILTER (WHERE status = 'PENDING') AS pending_transactions,
            COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_transactions
        FROM transactions
        """
    )
    row = conn.execute(sql).fetchone()

    if not row:
        return {
            "total_transactions": 0,
            "total_volume": Decimal("0"),
            "completed_transactions": 0,
            "pending_transactions": 0,
            "failed_transactions": 0,
            "avg_transaction_amount": Decimal("0"),
        }

    m = row._mapping
    return {
        "total_transactions": m["total_transactions"],
        "total_volume": Decimal(str(m["total_volume"])),
        "completed_transactions": m["completed_transactions"],
        "pending_transactions": m["pending_transactions"],
        "failed_transactions": m["failed_transactions"],
        "avg_transaction_amount": Decimal(str(m["avg_transaction_amount"])),
    }
