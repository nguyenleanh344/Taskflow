from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    try:
        access_token, refresh_token = await service.login(data)

    except ValueError as exc:
        if str(exc) == "User is inactive":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    
@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_access_token(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    try:
        access_token, refresh_token = (
            await service.refresh_access_token(
                data.refresh_token
            )
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )