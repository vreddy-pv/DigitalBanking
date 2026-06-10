import httpx

from app.auth.jwt_validator import UserContext
from app.config import settings

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

# ── Tool handlers — call complaint-service :8011 ──────────────────────────

async def raise_complaint(
    user_context: UserContext,
    transaction_id: str,
    account_id: str,
    complaint_type: str,
    description: str,
    product_line: str,
    **_,
) -> dict:
    payload = {
        "userId": user_context.user_id,
        "accountId": account_id,
        "transactionId": transaction_id,
        "productLine": product_line,
        "complaintType": complaint_type,
        "description": description,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.complaint_service_url}/api/v1/complaints",
            json=payload,
        )
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


async def get_complaint_status(
    user_context: UserContext, ticket_id: str, **_
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.complaint_service_url}/api/v1/complaints/{ticket_id}",
            params={"userId": user_context.user_id},
        )
        if resp.status_code == 404:
            return {"error": f"Ticket {ticket_id} not found. Please check the ticket ID and try again."}
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


HANDLERS: dict = {
    "raise_complaint": raise_complaint,
    "get_complaint_status": get_complaint_status,
}
