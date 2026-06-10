import httpx

from app.auth.jwt_validator import UserContext
from app.config import settings

# ── Tool schema definitions (Anthropic format) ──────────────────────────────

DEFINITIONS = [
    {
        "name": "get_customer_accounts",
        "description": (
            "Retrieve all bank accounts (savings, current) belonging to the authenticated customer. "
            "Returns account numbers, types, balances, and statuses. "
            "Call this first whenever the user asks about their balance or accounts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_account_balance",
        "description": (
            "Retrieve the current balance and details for a specific account by its account number. "
            "Use when the user specifies an account number or after listing accounts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The bank account number (e.g. ACC-00001234).",
                }
            },
            "required": ["account_number"],
        },
    },
]

# ── Tool handlers ────────────────────────────────────────────────────────────

async def get_customer_accounts(user_context: UserContext, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: resolve customerId from userId
        resp = await client.get(
            f"{settings.account_service_url}/api/v1/accounts/customer/user/{user_context.user_id}"
        )
        if resp.status_code == 404:
            return {"error": "No customer profile found for this user. Please register first."}
        resp.raise_for_status()
        customer = resp.json()["data"]
        customer_id = customer["customerId"]

        # Step 2: get all accounts for this customer
        resp2 = await client.get(
            f"{settings.account_service_url}/api/v1/accounts/customer/{customer_id}/accounts"
        )
        resp2.raise_for_status()
        accounts = resp2.json()["data"]

    return {
        "customer_name": customer.get("fullName"),
        "accounts": [
            {
                "account_id": a.get("accountId"),
                "account_number": a.get("accountNumber"),
                "account_type": a.get("accountType"),
                "balance": a.get("balance"),
                "currency": a.get("currency", "INR"),
                "status": a.get("status"),
            }
            for a in accounts
        ],
    }


async def get_account_balance(user_context: UserContext, account_number: str, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.account_service_url}/api/v1/accounts/number/{account_number}"
        )
        if resp.status_code == 404:
            return {"error": f"Account {account_number} not found."}
        resp.raise_for_status()
        a = resp.json()["data"]

    return {
        "account_id": a.get("accountId"),
        "account_number": a.get("accountNumber"),
        "account_type": a.get("accountType"),
        "balance": a.get("balance"),
        "available_balance": a.get("availableBalance", a.get("balance")),
        "currency": a.get("currency", "INR"),
        "status": a.get("status"),
    }


HANDLERS: dict = {
    "get_customer_accounts": get_customer_accounts,
    "get_account_balance": get_account_balance,
}
