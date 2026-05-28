from datetime import datetime
from uuid import UUID
import uuid
from pydantic import EmailStr, Field,model_validator

from app.schemas.common import ORMBase

class UserBase(ORMBase):
    email : EmailStr
    full_name : str | None = None
    username : str
    phone : str
    is_active: bool = True
    is_superuser: bool = False
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @model_validator(mode="after")
    def verify_password_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    
class UserUpdate(ORMBase):
    email : EmailStr | None = None
    full_name : str | None = None
    username : str | None = None
    phone : str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    
    
class UserRead(UserBase):
    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserInDB(UserRead):
    hashed_password: str