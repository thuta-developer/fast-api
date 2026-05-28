from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, UserServiceDep, require_permission
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UserAdminCreate, UserRead, UserUpdate

router = APIRouter()

ReadUsers = Annotated[User, Depends(require_permission("users.read"))]
CreateUsers = Annotated[User, Depends(require_permission("users.create"))]
UpdateUsers = Annotated[User, Depends(require_permission("users.update"))]
DeleteUsers = Annotated[User, Depends(require_permission("users.delete"))]

@router.get("/me", response_model=UserRead)
async def get_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserAdminCreate,
    _: CreateUsers,
    service: UserServiceDep,
) -> UserRead:
    return await service.admin_create_user(data)

@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    _: ReadUsers,
    service: UserServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(2, ge=1, le=100),

) -> PaginatedResponse[UserRead]:
    return await service.list_users(page=page, size=size)



@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    _: ReadUsers,
    service: UserServiceDep,
) -> UserRead:
    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    _: UpdateUsers,
    service: UserServiceDep,
) -> UserRead:
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    _: DeleteUsers,
    service: UserServiceDep,
) -> MessageResponse:
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
