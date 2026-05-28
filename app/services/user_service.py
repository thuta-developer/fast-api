import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.token import Token
from app.schemas.user import UserAdminCreate, UserCreate, UserRead, UserUpdate
from uuid import UUID



class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> UserRead:
        if await self.repo.email_exists(data.email):
            raise ConflictException("Email already exists")

        user = await self.repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=get_password_hash(data.password),
            is_superuser=False,
            is_active=True,
        )
        return UserRead.model_validate(user)

    async def admin_create_user(self, data: UserAdminCreate) -> UserRead:
        if await self.repo.email_exists(data.email):
            raise ConflictException("Email already exists")

        user = await self.repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=get_password_hash(data.password),
            is_superuser=data.is_superuser,
            is_active=data.is_active,
        )
        return UserRead.model_validate(user)
    
    async def authenticate(self, email: str, password: str ) -> Token:
        user = await self.repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException("Inactive user")
        
        token = create_access_token(subject=user.id)
        return Token(access_token=token)
    
    async def get_user(self, user_id: UUID) -> UserRead:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User")
        return UserRead.model_validate(user)
    
    async def list_users(self, page: int = 1, size: int = 20) -> PaginatedResponse[UserRead]:
        skip = (page - 1) * size
        users, total = await self.repo.list_users(skip=skip, limit=size)
        return PaginatedResponse(
            items=[UserRead.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total else 0,
        )
        
    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User")

        if data.email and await self.repo.email_exists(data.email, exclude_id=user_id):
            raise ConflictException("Email already in use")

        updated = await self.repo.update(user, data)
        return UserRead.model_validate(updated)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User")
        await self.repo.delete(user)
    
        

        
