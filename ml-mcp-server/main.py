import logging
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

LOAN_SERVICE_URL = os.getenv("LOAN_SERVICE_URL", "http://localhost:8012")

app = FastAPI(title="ML (Mortgage Loans) MCP Adapter", version="1.0.0")

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_mortgage_loans",
        "description": (
            "List all active mortgage loans (home loan, LAP, construction loan) for the customer. "
            "Call this first to get loan IDs before checking EMI or prepayment details."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_emi_schedule",
        "description": (
            "Retrieve the upcoming EMI amortisation schedule for a mortgage loan. "
            "Shows principal, interest, and balance after each EMI."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {"type": "string", "description": "The mortgage loan UUID."},
                "upcoming_months": {
                    "type": "integer",
                    "description": "Number of upcoming EMIs to show (default 3).",
                    "default": 3,
                },
            },
            "required": ["loan_id"],
        },
    },
    {
        "name": "get_prepayment_quote",
        "description": (
            "Get the prepayment amount, penalty (if any), and net payoff figure for a mortgage loan. "
            "Remind the customer the quote is indicative and valid for 7 days."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {"type": "string", "description": "The mortgage loan UUID."}
            },
            "required": ["loan_id"],
        },
    },
]

# ── Business logic ────────────────────────────────────────────────────────────


async def _get_mortgage_loans(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LOAN_SERVICE_URL}/api/v1/loans/{user_id}/mortgage")
        resp.raise_for_status()
        loans = resp.json()["data"]

    if not loans:
        return {"message": "No active mortgage loans found for your account.", "loans": []}
    return {"loans": loans, "count": len(loans)}


async def _get_emi_schedule(loan_id: str, upcoming_months: int = 3) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{LOAN_SERVICE_URL}/api/v1/loans/{loan_id}/emi-schedule",
            params={"upcomingMonths": upcoming_months},
        )
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        resp.raise_for_status()
        schedule = resp.json()["data"]

    return {"loan_id": loan_id, "upcoming_emis": schedule, "count": len(schedule)}


async def _get_prepayment_quote(loan_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LOAN_SERVICE_URL}/api/v1/loans/{loan_id}/prepayment-quote")
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        resp.raise_for_status()
        return resp.json()["data"]


# ── REST API endpoints ────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "UP", "service": "ml-mcp-server", "version": "1.0.0"}


@app.get("/api/tools")
def list_tools():
    return {"tools": TOOLS, "count": len(TOOLS), "server": "ml-mcp-server"}


@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    body = await request.json()
    user_id: str = body.get("user_id", "")
    if not user_id:
        return JSONResponse({"error": "user_id is required"}, status_code=400)

    try:
        if tool_name == "get_mortgage_loans":
            return await _get_mortgage_loans(user_id)
        elif tool_name == "get_emi_schedule":
            loan_id = body.get("loan_id", "")
            if not loan_id:
                return JSONResponse({"error": "loan_id is required"}, status_code=400)
            return await _get_emi_schedule(loan_id, body.get("upcoming_months", 3))
        elif tool_name == "get_prepayment_quote":
            loan_id = body.get("loan_id", "")
            if not loan_id:
                return JSONResponse({"error": "loan_id is required"}, status_code=400)
            return await _get_prepayment_quote(loan_id)
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
