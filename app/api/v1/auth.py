from fastapi import APIRouter, Depends
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

    access_token, refresh_token = await service.login(data)

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

    access_token, refresh_token = await service.refresh_access_token(data.refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
