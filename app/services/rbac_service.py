import math
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.repositories.rbac_repository import RBACRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.rbac import (
    PermissionCreate,
    PermissionRead,
    PermissionUpdate,
    RoleCreate,
    RoleRead,
    RoleUpdate,
    RoleWithPermissions,
    UserRolesRead,
)


class RBACService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = RBACRepository(db)
        self.user_repo = UserRepository(db)

    async def list_roles(self, page: int = 1, size: int = 100) -> PaginatedResponse[RoleRead]:
        skip = (page - 1) * size
        roles, total = await self.repo.list_roles(skip=skip, limit=size)
        return PaginatedResponse(
            items=[RoleRead.model_validate(role) for role in roles],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total else 0,
        )

    async def create_role(self, data: RoleCreate) -> RoleRead:
        if await self.repo.get_role_by_name(data.name):
            raise ConflictException("Role name already exists")
        role = await self.repo.create_role(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
        )
        return RoleRead.model_validate(role)

    async def get_role(self, role_id: UUID) -> RoleWithPermissions:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        permissions = await self.repo.get_role_permissions(role_id)
        return RoleWithPermissions(
            **RoleRead.model_validate(role).model_dump(),
            permissions=[PermissionRead.model_validate(permission) for permission in permissions],
        )

    async def update_role(self, role_id: UUID, data: RoleUpdate) -> RoleRead:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        if data.name and data.name != role.name and await self.repo.get_role_by_name(data.name):
            raise ConflictException("Role name already exists")
        updated = await self.repo.update_role(role, data)
        return RoleRead.model_validate(updated)

    async def delete_role(self, role_id: UUID) -> None:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        await self.repo.delete_role(role)

    async def list_permissions(
        self, page: int = 1, size: int = 100
    ) -> PaginatedResponse[PermissionRead]:
        skip = (page - 1) * size
        permissions, total = await self.repo.list_permissions(skip=skip, limit=size)
        return PaginatedResponse(
            items=[PermissionRead.model_validate(permission) for permission in permissions],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total else 0,
        )

    async def create_permission(self, data: PermissionCreate) -> PermissionRead:
        if await self.repo.get_permission_by_code(data.code):
            raise ConflictException("Permission code already exists")
        permission = await self.repo.create_permission(
            code=data.code,
            name=data.name,
            description=data.description,
        )
        return PermissionRead.model_validate(permission)

    async def update_permission(self, permission_id: UUID, data: PermissionUpdate) -> PermissionRead:
        permission = await self.repo.get_permission_by_id(permission_id)
        if permission is None:
            raise NotFoundException("Permission")
        if (
            data.code
            and data.code != permission.code
            and await self.repo.get_permission_by_code(data.code)
        ):
            raise ConflictException("Permission code already exists")
        updated = await self.repo.update_permission(permission, data)
        return PermissionRead.model_validate(updated)

    async def delete_permission(self, permission_id: UUID) -> None:
        permission = await self.repo.get_permission_by_id(permission_id)
        if permission is None:
            raise NotFoundException("Permission")
        await self.repo.delete_permission(permission)

    async def assign_permission_to_role(
        self, role_id: UUID, permission_id: UUID
    ) -> RoleWithPermissions:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        permission = await self.repo.get_permission_by_id(permission_id)
        if permission is None:
            raise NotFoundException("Permission")
        await self.repo.assign_permission_to_role(role_id, permission_id)
        return await self.get_role(role_id)

    async def remove_permission_from_role(
        self, role_id: UUID, permission_id: UUID
    ) -> RoleWithPermissions:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        permission = await self.repo.get_permission_by_id(permission_id)
        if permission is None:
            raise NotFoundException("Permission")
        await self.repo.remove_permission_from_role(role_id, permission_id)
        return await self.get_role(role_id)

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> UserRolesRead:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User")
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        await self.repo.assign_role_to_user(user_id, role_id)
        return await self.get_user_roles(user_id)

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> UserRolesRead:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User")
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise NotFoundException("Role")
        await self.repo.remove_role_from_user(user_id, role_id)
        return await self.get_user_roles(user_id)

    async def get_user_roles(self, user_id: UUID) -> UserRolesRead:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User")
        roles = await self.repo.get_user_roles(user_id)
        return UserRolesRead(user_id=user_id, roles=[RoleRead.model_validate(role) for role in roles])
