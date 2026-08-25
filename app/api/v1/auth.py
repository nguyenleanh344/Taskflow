from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.core.unit_of_work import UnitOfWork, get_unit_of_work


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
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    service = AuthService(uow)

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
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    service = AuthService(uow)

    try:
        access_token, refresh_token = await service.refresh_access_token(
            data.refresh_token
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
