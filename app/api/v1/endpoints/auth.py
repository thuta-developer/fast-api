from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import LoginPayload, UserServiceDep, get_login_credentials
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserCreate, service: UserServiceDep) -> UserRead:
    return await service.register(data)


@router.post("/login", response_model=Token)
async def login(
    credentials: Annotated[LoginPayload, Depends(get_login_credentials)],
    service: UserServiceDep,
) -> Token:
    return await service.authenticate(credentials.email, credentials.password)
