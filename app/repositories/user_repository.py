from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserUpdate

class UserRepository:
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def list_users(self, *, skip: int = 0, limit: int = 2) -> tuple[list[User], int]:
        count_result = await self.db.execute(select(func.count()).select_from(User))
        total = count_result.scalar()
        
        result = await self.db.execute(select(User).order_by(User.created_at.desc()).offset(skip).limit(limit))
        users = result.scalars().all()
        
        return users, total
    
    async def create(self, *, email: str, username: str, full_name: str, phone: str, hashed_password: str, is_superuser: bool = False, is_active: bool = True) -> User:
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            hashed_password=hashed_password,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True, exclude={"password", "confirm_password"})
        for fields, value in update_data.items():
            setattr(user, fields, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()
        
    async def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        query = select(User.id).where(User.email == email)
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None