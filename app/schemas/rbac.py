from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMBase


class RoleBase(ORMBase):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(ORMBase):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class RoleRead(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PermissionBase(ORMBase):
    code: str = Field(..., min_length=3, max_length=120)
    name: str = Field(..., min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=255)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(ORMBase):
    code: str | None = Field(default=None, min_length=3, max_length=120)
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=255)


class PermissionRead(PermissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class RolePermissionAssign(ORMBase):
    permission_id: UUID


class UserRoleAssign(ORMBase):
    role_id: UUID


class RoleWithPermissions(RoleRead):
    permissions: list[PermissionRead]


class UserRolesRead(ORMBase):
    user_id: UUID
    roles: list[RoleRead]
