from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import RBACServiceDep, require_permission
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.rbac import (
    PermissionCreate,
    PermissionRead,
    PermissionUpdate,
    RoleCreate,
    RolePermissionAssign,
    RoleRead,
    RoleUpdate,
    RoleWithPermissions,
    UserRoleAssign,
    UserRolesRead,
)

router = APIRouter()

ManageRoles = Annotated[User, Depends(require_permission("roles.manage"))]
ManagePermissions = Annotated[User, Depends(require_permission("permissions.manage"))]
ManageUserRoles = Annotated[User, Depends(require_permission("users.assign_roles"))]


@router.get("/roles", response_model=PaginatedResponse[RoleRead])
async def list_roles(
    _: ManageRoles,
    service: RBACServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=200),
) -> PaginatedResponse[RoleRead]:
    return await service.list_roles(page=page, size=size)


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    _: ManageRoles,
    service: RBACServiceDep,
) -> RoleRead:
    return await service.create_role(data)


@router.get("/roles/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: UUID,
    _: ManageRoles,
    service: RBACServiceDep,
) -> RoleWithPermissions:
    return await service.get_role(role_id)


@router.patch("/roles/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    _: ManageRoles,
    service: RBACServiceDep,
) -> RoleRead:
    return await service.update_role(role_id, data)


@router.delete("/roles/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: UUID,
    _: ManageRoles,
    service: RBACServiceDep,
) -> MessageResponse:
    await service.delete_role(role_id)
    return MessageResponse(message="Role deleted successfully")


@router.post("/roles/{role_id}/permissions", response_model=RoleWithPermissions)
async def assign_permission_to_role(
    role_id: UUID,
    data: RolePermissionAssign,
    _: ManageRoles,
    service: RBACServiceDep,
) -> RoleWithPermissions:
    return await service.assign_permission_to_role(role_id, data.permission_id)


@router.delete("/roles/{role_id}/permissions/{permission_id}", response_model=RoleWithPermissions)
async def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    _: ManageRoles,
    service: RBACServiceDep,
) -> RoleWithPermissions:
    return await service.remove_permission_from_role(role_id, permission_id)


@router.get("/permissions", response_model=PaginatedResponse[PermissionRead])
async def list_permissions(
    _: ManagePermissions,
    service: RBACServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=200),
) -> PaginatedResponse[PermissionRead]:
    return await service.list_permissions(page=page, size=size)


@router.post(
    "/permissions",
    response_model=PermissionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    data: PermissionCreate,
    _: ManagePermissions,
    service: RBACServiceDep,
) -> PermissionRead:
    return await service.create_permission(data)


@router.patch("/permissions/{permission_id}", response_model=PermissionRead)
async def update_permission(
    permission_id: UUID,
    data: PermissionUpdate,
    _: ManagePermissions,
    service: RBACServiceDep,
) -> PermissionRead:
    return await service.update_permission(permission_id, data)


@router.delete("/permissions/{permission_id}", response_model=MessageResponse)
async def delete_permission(
    permission_id: UUID,
    _: ManagePermissions,
    service: RBACServiceDep,
) -> MessageResponse:
    await service.delete_permission(permission_id)
    return MessageResponse(message="Permission deleted successfully")


@router.get("/users/{user_id}/roles", response_model=UserRolesRead)
async def get_user_roles(
    user_id: UUID,
    _: ManageUserRoles,
    service: RBACServiceDep,
) -> UserRolesRead:
    return await service.get_user_roles(user_id)


@router.post("/users/{user_id}/roles", response_model=UserRolesRead)
async def assign_role_to_user(
    user_id: UUID,
    data: UserRoleAssign,
    _: ManageUserRoles,
    service: RBACServiceDep,
) -> UserRolesRead:
    return await service.assign_role_to_user(user_id, data.role_id)


@router.delete("/users/{user_id}/roles/{role_id}", response_model=UserRolesRead)
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    _: ManageUserRoles,
    service: RBACServiceDep,
) -> UserRolesRead:
    return await service.remove_role_from_user(user_id, role_id)
