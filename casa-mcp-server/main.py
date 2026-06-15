import logging
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8002")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8003")

app = FastAPI(title="CASA MCP Adapter", version="1.0.0")

# ── Tool definitions (Claude-compatible, user_id excluded — injected by agent) ──

TOOLS = [
    {
        "name": "get_customer_accounts",
        "description": (
            "Retrieve all bank accounts (savings, current) for the authenticated customer. "
            "Returns account numbers, types, balances, and statuses. "
            "Call this first whenever the user asks about their balance or accounts."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
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
    {
        "name": "get_recent_transactions",
        "description": (
            "Retrieve recent transactions for a specific account. "
            "Returns type, amount, date, status, and description. "
            "Use after identifying the account ID from get_customer_accounts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "UUID of the account."},
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
            "Use when the customer asks about a specific transaction or before raising a complaint."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "UUID of the transaction."}
            },
            "required": ["transaction_id"],
        },
    },
]

# ── Business logic ────────────────────────────────────────────────────────────


async def _get_customer_accounts(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{ACCOUNT_SERVICE_URL}/api/v1/accounts/customer/user/{user_id}")
        if resp.status_code == 404:
            return {"error": "No customer profile found for this user."}
        resp.raise_for_status()
        customer = resp.json()["data"]
        customer_id = customer["customerId"]

        resp2 = await client.get(
            f"{ACCOUNT_SERVICE_URL}/api/v1/accounts/customer/{customer_id}/accounts"
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


async def _get_account_balance(account_number: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{ACCOUNT_SERVICE_URL}/api/v1/accounts/number/{account_number}")
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


async def _get_recent_transactions(account_id: str, limit: int = 10) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/account/{account_id}"
        )
        if resp.status_code == 404:
            return {"error": f"No transactions found for account {account_id}."}
        resp.raise_for_status()
        all_txns = resp.json()["data"]

    txns = all_txns[:limit]
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


async def _get_transaction_detail(transaction_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}"
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


# ── REST API endpoints ────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "UP", "service": "casa-mcp-server", "version": "1.0.0"}


@app.get("/api/tools")
def list_tools():
    return {"tools": TOOLS, "count": len(TOOLS), "server": "casa-mcp-server"}


@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    body = await request.json()
    user_id: str = body.get("user_id", "")
    if not user_id:
        return JSONResponse({"error": "user_id is required"}, status_code=400)

    try:
        if tool_name == "get_customer_accounts":
            return await _get_customer_accounts(user_id)
        elif tool_name == "get_account_balance":
            account_number = body.get("account_number", "")
            if not account_number:
                return JSONResponse({"error": "account_number is required"}, status_code=400)
            return await _get_account_balance(account_number)
        elif tool_name == "get_recent_transactions":
            account_id = body.get("account_id", "")
            if not account_id:
                return JSONResponse({"error": "account_id is required"}, status_code=400)
            return await _get_recent_transactions(account_id, body.get("limit", 10))
        elif tool_name == "get_transaction_detail":
            transaction_id = body.get("transaction_id", "")
            if not transaction_id:
                return JSONResponse({"error": "transaction_id is required"}, status_code=400)
            return await _get_transaction_detail(transaction_id)
        else:
            return JSONResponse({"error": f"Unknown tool: {tool_name}"}, status_code=404)

    except httpx.HTTPStatusError as e:
        logger.error("Backend error for tool %s: %s", tool_name, e)
        return JSONResponse(
            {"error": f"Backend service returned {e.response.status_code}"}, status_code=502
        )
    except Exception as e:
        logger.exception("Unexpected error calling tool %s", tool_name)
        return JSONResponse({"error": str(e)}, status_code=500)
