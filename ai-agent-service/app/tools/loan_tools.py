import httpx

from app.auth.jwt_validator import UserContext
from app.config import settings

# ── Tool schema definitions ───────────────────────────────────────────────

ML_DEFINITIONS = [
    {
        "name": "get_mortgage_loans",
        "description": "List all active mortgage loans (home loan, LAP, construction loan) for the customer.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_emi_schedule",
        "description": "Retrieve the upcoming EMI amortisation schedule for a mortgage loan.",
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
        "description": "Get the prepayment amount, penalty (if any), and net payoff figure for a mortgage loan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {"type": "string", "description": "The mortgage loan UUID."}
            },
            "required": ["loan_id"],
        },
    },
]

USL_DEFINITIONS = [
    {
        "name": "get_unsecured_loans",
        "description": "List all active unsecured loans (personal loan, credit card, overdraft) for the customer.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_payment_due",
        "description": "Get the next payment due date, minimum payment, and total outstanding for an unsecured loan or credit card.",
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
        "description": "Get the credit limit, utilised amount, and available credit for a revolving product (credit card or OD).",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {"type": "string", "description": "The credit card or OD account UUID."}
            },
            "required": ["loan_id"],
        },
    },
]

# ── Tool handlers — call loan-service :8012 ───────────────────────────────


async def get_mortgage_loans(user_context: UserContext, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.loan_service_url}/api/v1/loans/{user_context.user_id}/mortgage"
        )
        resp.raise_for_status()
        loans = resp.json()["data"]

    if not loans:
        return {"message": "No active mortgage loans found for your account.", "loans": []}
    return {"loans": loans, "count": len(loans)}


async def get_emi_schedule(
    user_context: UserContext, loan_id: str, upcoming_months: int = 3, **_
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.loan_service_url}/api/v1/loans/{loan_id}/emi-schedule",
            params={"upcomingMonths": upcoming_months},
        )
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        resp.raise_for_status()
        schedule = resp.json()["data"]

    return {"loan_id": loan_id, "upcoming_emis": schedule, "count": len(schedule)}


async def get_prepayment_quote(user_context: UserContext, loan_id: str, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.loan_service_url}/api/v1/loans/{loan_id}/prepayment-quote"
        )
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        resp.raise_for_status()
        return resp.json()["data"]


async def get_unsecured_loans(user_context: UserContext, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.loan_service_url}/api/v1/loans/{user_context.user_id}/unsecured"
        )
        resp.raise_for_status()
        loans = resp.json()["data"]

    if not loans:
        return {"message": "No active unsecured loans found for your account.", "loans": []}
    return {"loans": loans, "count": len(loans)}


async def get_payment_due(user_context: UserContext, loan_id: str, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.loan_service_url}/api/v1/loans/{loan_id}/payment-due"
        )
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        resp.raise_for_status()
        return resp.json()["data"]


async def get_credit_limit(user_context: UserContext, loan_id: str, **_) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.loan_service_url}/api/v1/loans/{loan_id}/credit-limit"
        )
        if resp.status_code == 404:
            return {"error": f"Loan {loan_id} not found."}
        if resp.status_code == 400:
            body = resp.json()
            return {"error": body.get("message", "Not a revolving product.")}
        resp.raise_for_status()
        return resp.json()["data"]


ML_HANDLERS: dict = {
    "get_mortgage_loans": get_mortgage_loans,
    "get_emi_schedule": get_emi_schedule,
    "get_prepayment_quote": get_prepayment_quote,
}

USL_HANDLERS: dict = {
    "get_unsecured_loans": get_unsecured_loans,
    "get_payment_due": get_payment_due,
    "get_credit_limit": get_credit_limit,
}
