import httpx

from app.auth.jwt_validator import UserContext
from app.config import settings

# ── Tool schema definitions ───────────────────────────────────────────────

DEFINITIONS = [
    {
        "name": "get_recent_transactions",
        "description": (
            "Retrieve recent transactions for a specific account. "
            "Returns transaction type, amount, date, status, and description. "
            "Use after identifying the account ID from get_customer_accounts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The UUID of the account.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of transactions to return (1–50). Defaults to 10.",
                    "default": 10,
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_transaction_detail",
        "description": (
            "Retrieve full detail for a single transaction by its ID. "
            "Use this when a customer asks about a specific transaction or before raising a complaint."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "The UUID of the transaction.",
                }
            },
            "required": ["transaction_id"],
        },
    },
]

# ── Tool handlers ─────────────────────────────────────────────────────────

async def get_recent_transactions(
    user_context: UserContext, account_id: str, limit: int = 10, **_
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.transaction_service_url}/api/v1/transactions/account/{account_id}"
        )
        if resp.status_code == 404:
            return {"error": f"No transactions found for account {account_id}."}
        resp.raise_for_status()
        all_txns = resp.json()["data"]

    txns = all_txns[:limit] if len(all_txns) > limit else all_txns
    return {
        "account_id": account_id,
        "total_returned": len(txns),
        "transactions": [
            {
                "transaction_id": t.get("id"),
                "type": t.get("type"),
                "amount": t.get("amount"),
                "currency": t.get("currency", "INR"),
                "status": t.get("status"),
                "description": t.get("description"),
                "created_at": t.get("createdAt"),
                "from_account": t.get("fromAccountId"),
                "to_account": t.get("toAccountId"),
            }
            for t in txns
        ],
    }


async def get_transaction_detail(
    user_context: UserContext, transaction_id: str, **_
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.transaction_service_url}/api/v1/transactions/{transaction_id}"
        )
        if resp.status_code == 404:
            return {"error": f"Transaction {transaction_id} not found."}
        resp.raise_for_status()
        t = resp.json()["data"]

    return {
        "transaction_id": t.get("id"),
        "type": t.get("type"),
        "amount": t.get("amount"),
        "currency": t.get("currency", "INR"),
        "status": t.get("status"),
        "description": t.get("description"),
        "request_id": t.get("requestId"),
        "from_account": t.get("fromAccountId"),
        "to_account": t.get("toAccountId"),
        "created_at": t.get("createdAt"),
        "updated_at": t.get("updatedAt"),
    }


HANDLERS: dict = {
    "get_recent_transactions": get_recent_transactions,
    "get_transaction_detail": get_transaction_detail,
}
