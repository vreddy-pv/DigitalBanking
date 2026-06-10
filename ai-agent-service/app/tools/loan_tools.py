"""
Loan tools — stubs until loan-service (:8007) is built.
Replace the stub implementations with real HTTP calls once the service is live.
"""
from app.auth.jwt_validator import UserContext

# ── Tool schema definitions ───────────────────────────────────────────────

ML_DEFINITIONS = [
    {
        "name": "get_mortgage_loans",
        "description": "List all active mortgage loans (home loan, LAP, construction loan) for the customer.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_emi_schedule",
        "description": "Retrieve the full EMI amortisation schedule for a mortgage loan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_id": {"type": "string", "description": "The mortgage loan ID."},
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
                "loan_id": {"type": "string", "description": "The mortgage loan ID."}
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
                "loan_id": {"type": "string", "description": "The loan or credit card ID."}
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
                "loan_id": {"type": "string", "description": "The credit card or OD account ID."}
            },
            "required": ["loan_id"],
        },
    },
]

# ── Stub handlers ─────────────────────────────────────────────────────────

_STUB_NOTE = "Loan Service is under construction. This is sample data."


async def get_mortgage_loans(user_context: UserContext, **_) -> dict:
    return {
        "note": _STUB_NOTE,
        "loans": [
            {
                "loan_id": "ML-20240001",
                "product": "Home Loan",
                "disbursed_amount": 5000000,
                "outstanding_principal": 4250000,
                "interest_rate": 8.65,
                "tenure_months": 240,
                "emi": 44067,
                "next_emi_date": "2026-07-05",
                "status": "ACTIVE",
                "currency": "INR",
            }
        ],
    }


async def get_emi_schedule(
    user_context: UserContext, loan_id: str, upcoming_months: int = 3, **_
) -> dict:
    return {
        "note": _STUB_NOTE,
        "loan_id": loan_id,
        "upcoming_emis": [
            {"month": f"2026-0{7 + i}", "emi": 44067, "principal": 12500, "interest": 31567, "balance_after": 4237500 - i * 12500}
            for i in range(upcoming_months)
        ],
    }


async def get_prepayment_quote(user_context: UserContext, loan_id: str, **_) -> dict:
    return {
        "note": _STUB_NOTE,
        "loan_id": loan_id,
        "outstanding_principal": 4250000,
        "accrued_interest": 12345,
        "prepayment_penalty": 0,
        "net_payoff_amount": 4262345,
        "valid_until": "2026-06-17",
        "currency": "INR",
    }


async def get_unsecured_loans(user_context: UserContext, **_) -> dict:
    return {
        "note": _STUB_NOTE,
        "loans": [
            {
                "loan_id": "PL-20240101",
                "product": "Personal Loan",
                "disbursed_amount": 500000,
                "outstanding": 320000,
                "emi": 11500,
                "next_due_date": "2026-07-10",
                "status": "ACTIVE",
                "currency": "INR",
            }
        ],
    }


async def get_payment_due(user_context: UserContext, loan_id: str, **_) -> dict:
    return {
        "note": _STUB_NOTE,
        "loan_id": loan_id,
        "next_due_date": "2026-07-10",
        "minimum_payment": 11500,
        "total_outstanding": 320000,
        "overdue_amount": 0,
        "currency": "INR",
    }


async def get_credit_limit(user_context: UserContext, loan_id: str, **_) -> dict:
    return {
        "note": _STUB_NOTE,
        "loan_id": loan_id,
        "credit_limit": 200000,
        "utilised": 45000,
        "available": 155000,
        "currency": "INR",
    }


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
