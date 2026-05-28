from typing import Annotated

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class LoginPayload(BaseModel):
    email: str
    password: str
    
async def get_login_credentials(request: Request) -> LoginPayload:
    # နည်းလမ်း ၁ - JSON အဖြစ် အရင်ဦးဆုံး ကြိုးစားဖတ်ကြည့်မည်
    try:
        body = await request.json()
        return LoginPayload(**body)
    except Exception:
        pass  # JSON ဖတ်လို့မရလျှင် အောက်က Form data အပိုင်းသို့ ဆက်သွားမည်

    # နည်းလမ်း ၂ - Form Data (x-www-form-urlencoded) အဖြစ် ထပ်မံကြိုးစားမည်
    try:
        form = await request.form()
        email = form.get("email")
        password = form.get("password")
        
        if email and password:
            return LoginPayload(email=str(email), password=str(password))
    except Exception:
        pass
    
    # ပုံစံနှစ်မျိုးလုံး ဖတ်လို့မရလျှင် Error ထုတ်မည်
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid request format. Please provide valid JSON or Form data with username and password.",
    )

DbSession = Annotated[AsyncSession, Depends(get_db)]

def get_user_service(db: DbSession) -> UserService:
    return UserService(db)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

async def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise UnauthorizedException()
    
    repo = UserRepository(db)
    user = await repo.get_by_id(UUID(user_id))
    if user is None:
        raise UnauthorizedException()
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise UnauthorizedException("Not enough permissions")
    return current_user

CurrentSuperuser = Annotated[User, Depends(get_current_superuser)]