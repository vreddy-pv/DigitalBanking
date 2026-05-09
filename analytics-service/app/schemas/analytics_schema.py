from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class StatementRow(BaseModel):
    id: UUID
    type: str
    amount: Decimal
    status: str
    description: Optional[str] = None
    created_at: datetime
    direction: str  # "CREDIT" or "DEBIT"


class StatementResponse(BaseModel):
    account_id: UUID
    page: int
    page_size: int
    total: int
    items: List[StatementRow]


class AccountSummary(BaseModel):
    account_id: UUID
    month: str
    total_credits: Decimal
    total_debits: Decimal
    net: Decimal
    transaction_count: int


class SpendingByType(BaseModel):
    type: str
    total_amount: Decimal
    transaction_count: int
    percentage: float


class TrialBalanceLine(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    total_debits: Decimal
    total_credits: Decimal
    balance: Decimal


class JournalEntryRow(BaseModel):
    id: UUID
    gl_account_id: UUID
    gl_account_code: str
    gl_account_name: str
    debit: Decimal
    credit: Decimal
    timestamp: datetime


class PlatformSummary(BaseModel):
    total_transactions: int
    total_volume: Decimal
    completed_transactions: int
    pending_transactions: int
    failed_transactions: int
    avg_transaction_amount: Decimal
