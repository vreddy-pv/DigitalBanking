import logging
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

LOAN_SERVICE_URL = os.getenv("LOAN_SERVICE_URL", "http://localhost:8012")

app = FastAPI(title="CUL (Credit & Unsecured Loans) MCP Adapter", version="1.0.0")

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_unsecured_loans",
        "description": (
            "List all active unsecured loans (personal loan, credit card, overdraft) for the customer. "
            "Call this first to get loan IDs before checking payment or credit limit details."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_payment_due",
        "description": (
            "Get the next payment due date, minimum payment, and total outstanding "
            "for an unsecured loan or credit card."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {"type": "string", "description": "The loan or credit card UUID."}
            },
            "required": ["loan_id"],
        },
    },
    {
        "name": "get_credit_limit",
        "description": (
            "Get the credit limit, utilised amount, and available credit "
            "for a revolving product (credit card or overdraft)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {
                    "type": "string",
                    "description": "The credit card or OD account UUID.",
                }
            },
            "required": ["loan_id"],
        },
    },
]

# ── Business logic ────────────────────────────────────────────────────────────


async def _get_unsecured_loans(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LOAN_SERVICE_URL}/api/v1/loans/{user_id}/unsecured")
        resp.raise_for_status()
        loans = resp.json()["data"]

    if not loans:
        return {"message": "No active unsecured loans found for your account.", "loans": []}
    return {"loans": loans, "count": len(loans)}


async def _get_payment_due(loan_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LOAN_SERVICE_URL}/api/v1/loans/{loan_id}/payment-due")
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        resp.raise_for_status()
        return resp.json()["data"]


async def _get_credit_limit(loan_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LOAN_SERVICE_URL}/api/v1/loans/{loan_id}/credit-limit")
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        if resp.status_code == 400:
            body = resp.json()
            return {"error": body.get("message", "Not a revolving product.")}
        resp.raise_for_status()
        return resp.json()["data"]


# ── REST API endpoints ────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "UP", "service": "cul-mcp-server", "version": "1.0.0"}


@app.get("/api/tools")
def list_tools():
    return {"tools": TOOLS, "count": len(TOOLS), "server": "cul-mcp-server"}


@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    body = await request.json()
    user_id: str = body.get("user_id", "")
    if not user_id:
        return JSONResponse({"error": "user_id is required"}, status_code=400)

    try:
        if tool_name == "get_unsecured_loans":
            return await _get_unsecured_loans(user_id)
        elif tool_name == "get_payment_due":
            loan_id = body.get("loan_id", "")
            if not loan_id:
                return JSONResponse({"error": "loan_id is required"}, status_code=400)
            return await _get_payment_due(loan_id)
        elif tool_name == "get_credit_limit":
            loan_id = body.get("loan_id", "")
            if not loan_id:
                return JSONResponse({"error": "loan_id is required"}, status_code=400)
            return await _get_credit_limit(loan_id)
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
