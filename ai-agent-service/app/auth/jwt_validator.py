from dataclasses import dataclass

import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()


@dataclass
class UserContext:
    user_id: str
    email: str
    full_name: str
    roles: list[str]


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> UserContext:
    token = credentials.credentials
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(
                f"{settings.auth_service_url}/api/v1/auth/validate",
                params={"token": token},
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    data = resp.json().get("data", {})
    return UserContext(
        user_id=data["userId"],
        email=data["email"],
        full_name=data["fullName"],
        roles=data.get("roles", []),
    )
