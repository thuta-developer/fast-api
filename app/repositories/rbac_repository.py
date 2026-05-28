from uuid import UUID

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rbac import Permission, Role, role_permissions, user_roles
from app.schemas.rbac import PermissionUpdate, RoleUpdate


class RBACRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_role_by_id(self, role_id: UUID) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def list_roles(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        
        count_result = await self.db.execute(select(func.count()).select_from(Role))
        total = count_result.scalar() or 0
        result = await self.db.execute(select(Role).order_by(Role.name).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def create_role(self, *, name: str, description: str | None, is_active: bool) -> Role:
        role = Role(name=name, description=description, is_active=is_active)
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def update_role(self, role: Role, data: RoleUpdate) -> Role:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role: Role) -> None:
        await self.db.delete(role)
        await self.db.flush()

    async def get_permission_by_id(self, permission_id: UUID) -> Permission | None:
        result = await self.db.execute(select(Permission).where(Permission.id == permission_id))
        return result.scalar_one_or_none()

    async def get_permission_by_code(self, code: str) -> Permission | None:
        result = await self.db.execute(select(Permission).where(Permission.code == code))
        return result.scalar_one_or_none()

    async def list_permissions(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[Permission], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Permission))
        total = count_result.scalar() or 0
        result = await self.db.execute(
            select(Permission).order_by(Permission.code).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create_permission(
        self, *, code: str, name: str, description: str | None
    ) -> Permission:
        permission = Permission(code=code, name=name, description=description)
        self.db.add(permission)
        await self.db.flush()
        await self.db.refresh(permission)
        return permission

    async def update_permission(self, permission: Permission, data: PermissionUpdate) -> Permission:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        await self.db.flush()
        await self.db.refresh(permission)
        return permission

    async def delete_permission(self, permission: Permission) -> None:
        await self.db.delete(permission)
        await self.db.flush()

    async def role_has_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        result = await self.db.execute(
            select(role_permissions.c.role_id).where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> None:
        if await self.role_has_permission(role_id, permission_id):
            return
        await self.db.execute(
            insert(role_permissions).values(role_id=role_id, permission_id=permission_id)
        )
        await self.db.flush()

    async def remove_permission_from_role(self, role_id: UUID, permission_id: UUID) -> None:
        await self.db.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id == permission_id,
            )
        )
        await self.db.flush()

    async def get_role_permissions(self, role_id: UUID) -> list[Permission]:
        result = await self.db.execute(
            select(Permission)
            .join(role_permissions, role_permissions.c.permission_id == Permission.id)
            .where(role_permissions.c.role_id == role_id)
            .order_by(Permission.code)
        )
        return list(result.scalars().all())

    async def user_has_role(self, user_id: UUID, role_id: UUID) -> bool:
        result = await self.db.execute(
            select(user_roles.c.user_id).where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> None:
        if await self.user_has_role(user_id, role_id):
            return
        await self.db.execute(insert(user_roles).values(user_id=user_id, role_id=role_id))
        await self.db.flush()

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> None:
        await self.db.execute(
            delete(user_roles).where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id,
            )
        )
        await self.db.flush()

    async def get_user_roles(self, user_id: UUID) -> list[Role]:
        result = await self.db.execute(
            select(Role)
            .join(user_roles, user_roles.c.role_id == Role.id)
            .where(user_roles.c.user_id == user_id)
            .order_by(Role.name)
        )
        return list(result.scalars().all())

    async def get_user_permission_codes(self, user_id: UUID) -> set[str]:
        result = await self.db.execute(
            select(Permission.code)
            .join(role_permissions, role_permissions.c.permission_id == Permission.id)
            .join(user_roles, user_roles.c.role_id == role_permissions.c.role_id)
            .join(Role, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id, Role.is_active.is_(True))
        )
        return set(result.scalars().all())
