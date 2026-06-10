"""
Complaint tools — stubs until complaint-service (:8006) is built.
Replace the stub implementations with real HTTP calls once the service is live.
"""
import uuid
from datetime import datetime, timezone

from app.auth.jwt_validator import UserContext

# ── Tool schema definitions ───────────────────────────────────────────────

DEFINITIONS = [
    {
        "name": "raise_complaint",
        "description": (
            "Raise a complaint for a transaction the customer disputes or does not recognise. "
            "Always call get_transaction_detail first and confirm details with the customer before calling this. "
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
                    "enum": ["CASA", "ML", "USL"],
                    "description": "Product line this complaint belongs to.",
                },
            },
            "required": ["transaction_id", "account_id", "complaint_type", "description", "product_line"],
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
]

# ── Stub handlers (replace with httpx calls once complaint-service is built) ─

_complaint_store: dict[str, dict] = {}  # in-memory store for stubs


async def raise_complaint(
    user_context: UserContext,
    transaction_id: str,
    account_id: str,
    complaint_type: str,
    description: str,
    product_line: str,
    **_,
) -> dict:
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    seq = str(len(_complaint_store) + 1).zfill(4)
    ticket_id = f"CMP-{date_str}-{seq}"

    _complaint_store[ticket_id] = {
        "ticket_id": ticket_id,
        "user_id": user_context.user_id,
        "transaction_id": transaction_id,
        "account_id": account_id,
        "complaint_type": complaint_type,
        "description": description,
        "product_line": product_line,
        "status": "ACCEPTED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sla_hours": {"FRAUD": 4, "UNAUTHORIZED": 4, "DISPUTE": 24, "ERROR": 48}.get(complaint_type, 48),
    }

    return {
        "ticket_id": ticket_id,
        "status": "ACCEPTED",
        "message": (
            f"Complaint registered successfully. Your ticket ID is {ticket_id}. "
            f"Our team will investigate and respond within "
            f"{_complaint_store[ticket_id]['sla_hours']} hours."
        ),
        "next_steps": "You will receive updates via your registered email. "
                      "You can also ask me to check your complaint status anytime.",
    }


async def get_complaint_status(
    user_context: UserContext, ticket_id: str, **_
) -> dict:
    complaint = _complaint_store.get(ticket_id)
    if not complaint:
        return {"error": f"Ticket {ticket_id} not found. Please check the ticket ID and try again."}

    if complaint["user_id"] != user_context.user_id:
        return {"error": "You are not authorised to view this complaint."}

    return {
        "ticket_id": complaint["ticket_id"],
        "status": complaint["status"],
        "complaint_type": complaint["complaint_type"],
        "product_line": complaint["product_line"],
        "created_at": complaint["created_at"],
        "sla_hours": complaint["sla_hours"],
        "message": f"Complaint {ticket_id} is currently {complaint['status']}.",
    }


HANDLERS: dict = {
    "raise_complaint": raise_complaint,
    "get_complaint_status": get_complaint_status,
}
