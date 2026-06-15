import logging
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

COMPLAINT_SERVICE_URL = os.getenv("COMPLAINT_SERVICE_URL", "http://localhost:8011")

app = FastAPI(title="Complaint MCP Adapter", version="1.0.0")

# product_line mapping: agent uses CUL, complaint-service backend expects USL
_PRODUCT_LINE_MAP = {"CUL": "USL"}

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "raise_complaint",
        "description": (
            "Raise a complaint for a transaction the customer disputes or does not recognise. "
            "Always show the transaction details and confirm with the customer before calling this. "
            "Returns a ticket_id the customer can use to track their complaint."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "UUID of the disputed transaction.",
                },
                "account_id": {
                    "type": "string",
                    "description": "UUID of the account the transaction belongs to.",
                },
                "complaint_type": {
                    "type": "string",
                    "enum": ["UNAUTHORIZED", "DISPUTE", "FRAUD", "ERROR"],
                    "description": (
                        "UNAUTHORIZED: customer never made this transaction; "
                        "DISPUTE: amount or merchant is wrong; "
                        "FRAUD: suspected fraudulent activity; "
                        "ERROR: system or posting error."
                    ),
                },
                "description": {
                    "type": "string",
                    "description": "Clear description of the issue in the customer's own words.",
                },
                "product_line": {
                    "type": "string",
                    "enum": ["CASA", "ML", "CUL"],
                    "description": "Product line this complaint belongs to.",
                },
            },
            "required": [
                "transaction_id",
                "account_id",
                "complaint_type",
                "description",
                "product_line",
            ],
        },
    },
    {
        "name": "get_complaint_status",
        "description": "Check the current status of an existing complaint using its ticket ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The complaint ticket ID returned when the complaint was raised.",
                }
            },
            "required": ["ticket_id"],
        },
    },
    {
        "name": "list_user_complaints",
        "description": (
            "List all complaints raised by the customer. "
            "Use when the customer asks to see all their open complaints or complaint history."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

# ── Business logic ────────────────────────────────────────────────────────────


async def _raise_complaint(
    user_id: str,
    transaction_id: str,
    account_id: str,
    complaint_type: str,
    description: str,
    product_line: str,
) -> dict:
    # Map CUL → USL for backend compatibility
    backend_product_line = _PRODUCT_LINE_MAP.get(product_line, product_line)
    payload = {
        "userId": user_id,
        "accountId": account_id,
        "transactionId": transaction_id,
        "productLine": backend_product_line,
        "complaintType": complaint_type,
        "description": description,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(f"{COMPLAINT_SERVICE_URL}/api/v1/complaints", json=payload)
        resp.raise_for_status()
        data = resp.json()["data"]

    sla_hours = {"FRAUD": 4, "UNAUTHORIZED": 4, "DISPUTE": 24, "ERROR": 48}.get(complaint_type, 48)
    return {
        "ticket_id": data["ticketId"],
        "status": data["status"],
        "sla_hours": sla_hours,
        "message": (
            f"Complaint registered. Your ticket ID is {data['ticketId']}. "
            f"Our team will investigate and respond within {sla_hours} hours."
        ),
        "next_steps": (
            "You will receive updates via your registered email. "
            "You can also ask me to check your complaint status anytime."
        ),
    }


async def _get_complaint_status(user_id: str, ticket_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{COMPLAINT_SERVICE_URL}/api/v1/complaints/{ticket_id}",
            params={"userId": user_id},
        )
        if resp.status_code == 404:
            return {"error": f"Ticket {ticket_id} not found. Please check the ticket ID."}
        if resp.status_code == 403:
            return {"error": "You are not authorised to view this complaint."}
        resp.raise_for_status()
        data = resp.json()["data"]

    return {
        "ticket_id": data["ticketId"],
        "status": data["status"],
        "complaint_type": data["complaintType"],
        "product_line": data["productLine"],
        "sla_deadline": data.get("slaDeadline"),
        "outcome": data.get("outcome"),
        "resolution": data.get("resolution"),
        "created_at": data.get("createdAt"),
        "message": f"Complaint {ticket_id} is currently {data['status']}.",
    }


async def _list_user_complaints(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{COMPLAINT_SERVICE_URL}/api/v1/complaints",
            params={"userId": user_id},
        )
        if resp.status_code == 404:
            return {"complaints": [], "count": 0, "message": "No complaints found."}
        resp.raise_for_status()
        complaints = resp.json().get("data", [])

    return {
        "complaints": [
            {
                "ticket_id": c.get("ticketId"),
                "status": c.get("status"),
                "complaint_type": c.get("complaintType"),
                "product_line": c.get("productLine"),
                "created_at": c.get("createdAt"),
                "outcome": c.get("outcome"),
            }
            for c in complaints
        ],
        "count": len(complaints),
    }


# ── REST API endpoints ────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "UP", "service": "complaint-mcp-server", "version": "1.0.0"}


@app.get("/api/tools")
def list_tools():
    return {"tools": TOOLS, "count": len(TOOLS), "server": "complaint-mcp-server"}


@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    body = await request.json()
    user_id: str = body.get("user_id", "")
    if not user_id:
        return JSONResponse({"error": "user_id is required"}, status_code=400)

    try:
        if tool_name == "raise_complaint":
            required = ["transaction_id", "account_id", "complaint_type", "description", "product_line"]
            missing = [f for f in required if not body.get(f)]
            if missing:
                return JSONResponse({"error": f"Missing fields: {missing}"}, status_code=400)
            return await _raise_complaint(
                user_id,
                body["transaction_id"],
                body["account_id"],
                body["complaint_type"],
                body["description"],
                body["product_line"],
            )
        elif tool_name == "get_complaint_status":
            ticket_id = body.get("ticket_id", "")
            if not ticket_id:
                return JSONResponse({"error": "ticket_id is required"}, status_code=400)
            return await _get_complaint_status(user_id, ticket_id)
        elif tool_name == "list_user_complaints":
            return await _list_user_complaints(user_id)
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
