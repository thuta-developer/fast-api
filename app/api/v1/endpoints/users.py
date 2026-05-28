from fastapi import APIRouter, Query, status

from app.api.deps import CurrentSuperuser, CurrentUser, UserServiceDep
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UserRead, UserUpdate
from uuid import UUID

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def get_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)

@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    _: CurrentSuperuser,
    service: UserServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),

) -> PaginatedResponse[UserRead]:
    return await service.list_users(page=page, size=size)



@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    _: CurrentSuperuser,
    service: UserServiceDep,
) -> UserRead:
    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    _: CurrentSuperuser,
    service: UserServiceDep,
) -> UserRead:
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    _: CurrentSuperuser,
    service: UserServiceDep,
) -> MessageResponse:
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
