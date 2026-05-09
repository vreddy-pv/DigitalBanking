from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.engine import Connection
from typing import List, Optional
from uuid import UUID

from app.database import get_transaction_db, get_ledger_db
from app.schemas.analytics_schema import (
    StatementResponse,
    AccountSummary,
    SpendingByType,
    TrialBalanceLine,
    JournalEntryRow,
    PlatformSummary,
)
from app.services import transaction_analytics, ledger_analytics

analytics_router = APIRouter(tags=["Analytics"])


@analytics_router.get(
    "/accounts/{account_id}/statement",
    response_model=StatementResponse,
)
def get_account_statement(
    account_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    conn: Connection = Depends(get_transaction_db),
):
    """Paginated transaction history for an account (FROM or TO), ordered by created_at DESC."""
    result = transaction_analytics.get_statement(
        conn=conn,
        account_id=str(account_id),
        page=page,
        page_size=page_size,
    )
    return result


@analytics_router.get(
    "/accounts/{account_id}/summary",
    response_model=AccountSummary,
)
def get_account_summary(
    account_id: UUID,
    month: Optional[str] = Query(default=None, description="Month in YYYY-MM format, e.g. 2026-05"),
    conn: Connection = Depends(get_transaction_db),
):
    """Monthly credit/debit summary for an account."""
    result = transaction_analytics.get_summary(
        conn=conn,
        account_id=str(account_id),
        month=month,
    )
    return result


@analytics_router.get(
    "/accounts/{account_id}/spending",
    response_model=List[SpendingByType],
)
def get_spending_breakdown(
    account_id: UUID,
    conn: Connection = Depends(get_transaction_db),
):
    """Spending breakdown by transaction type for an account."""
    result = transaction_analytics.get_spending_breakdown(
        conn=conn,
        account_id=str(account_id),
    )
    return result


@analytics_router.get(
    "/ledger/trial-balance",
    response_model=List[TrialBalanceLine],
)
def get_trial_balance(
    conn: Connection = Depends(get_ledger_db),
):
    """List all GL accounts with aggregated debit/credit totals from journal entries."""
    result = ledger_analytics.get_trial_balance(conn=conn)
    return result


@analytics_router.get(
    "/ledger/journal/{transaction_id}",
    response_model=List[JournalEntryRow],
)
def get_journal_entries(
    transaction_id: UUID,
    conn: Connection = Depends(get_ledger_db),
):
    """Journal entries for a specific transaction, joined with GL account details."""
    result = ledger_analytics.get_journal_entries_for_transaction(
        conn=conn,
        transaction_id=str(transaction_id),
    )
    return result


@analytics_router.get(
    "/summary",
    response_model=PlatformSummary,
)
def get_platform_summary(
    conn: Connection = Depends(get_transaction_db),
):
    """Platform-wide transaction statistics."""
    result = transaction_analytics.get_platform_summary(conn=conn)
    return result
