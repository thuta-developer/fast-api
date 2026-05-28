# FastAPI Project Guide for Django Developers

ဒီ guide က Django developer တစ်ယောက်အနေနဲ့ ဒီ FastAPI project ကို နားလည်လွယ်အောင် ရေးထားတာပါ။ Folder တစ်ခုချင်း၊ file တစ်ခုချင်း၊ code flow တစ်ခုချင်းကို Django နဲ့ နှိုင်းယှဉ်ပြီး ရှင်းပြထားပါတယ်။

## Big Picture

ဒီ project ရဲ့ request flow က အောက်ပါအတိုင်း သွားပါတယ်။

```text
HTTP Request
  -> app/main.py
  -> app/api/v1/router.py
  -> app/api/v1/endpoints/*.py
  -> app/api/deps.py
  -> app/services/*.py
  -> app/repositories/*.py
  -> app/models/*.py
  -> Database
  -> app/schemas/*.py
  -> HTTP Response
```

Django / DRF နဲ့ နှိုင်းယှဉ်ရင်:

```text
Django settings.py          -> app/core/config.py
Django urls.py              -> app/api/v1/router.py
Django views.py / DRF views -> app/api/v1/endpoints/*.py
DRF serializers.py          -> app/schemas/*.py
Django models.py            -> app/models/*.py
Django middleware           -> app/middleware/*.py
Django migrations           -> alembic/versions/*.py
Custom manager/queryset     -> app/repositories/*.py
Service layer               -> app/services/*.py
```

## Project Structure

```text
fast_api_project/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── health.py
│   │           └── users.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── middleware/
│   │   └── request_id.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── repositories/
│   │   └── user_repository.py
│   ├── schemas/
│   │   ├── common.py
│   │   ├── token.py
│   │   └── user.py
│   └── services/
│       └── user_service.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 7d5a575c7654_create_user_table_with_uuid.py
├── tests/
├── .env
├── Makefile
├── alembic.ini
├── guide.md
└── sql_app.db
```

## Root Files

### `.env`

Environment variables တွေထားတဲ့ file ပါ။ Django မှာ `settings.py` ထဲ hard-code မရေးဘဲ `.env` ကနေဖတ်သလိုမျိုးပါ။

ဥပမာ:

```env
APP_NAME=FastAPI Project
DATABASE_URL=sqlite+aiosqlite:///./sql_app.db
SECRET_KEY=...
```

ဒီ project မှာ `.env` ကို `app/core/config.py` က ဖတ်ပါတယ်။

### `Makefile`

Terminal command အတိုလေးတွေ သတ်မှတ်ထားတဲ့ file ပါ။

```makefile
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`make dev` လို့ run လိုက်ရင် FastAPI app ကို reload mode နဲ့ run ပါမယ်။

အဓိက commands:

```bash
make dev       # development server run
make run       # production-style server run
make migrate   # alembic migration apply
make migration msg="message"  # migration file generate
make test      # pytest run
make lint      # ruff lint check
make format    # ruff auto-fix + format
```

### `sql_app.db`

SQLite database file ပါ။ Django မှာ `db.sqlite3` နဲ့ တူပါတယ်။

### `alembic.ini`

Alembic migration tool ရဲ့ config file ပါ။ Django migration system အတွက် config နဲ့ဆင်တူပါတယ်။

## `app/main.py`

ဒီ file က FastAPI application ရဲ့ entry point ပါ။

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIDMiddleware
```

ဒီ imports တွေက:

- `FastAPI`: app object ဆောက်ဖို့
- `CORSMiddleware`: frontend domain တွေကို API ခေါ်ခွင့်ပေးဖို့
- `api_router`: endpoint routers တွေ စုပေးထားတဲ့ router
- `get_settings`: `.env` / config values ဖတ်ဖို့
- `setup_logging`: logging setup လုပ်ဖို့
- `RequestIDMiddleware`: request တစ်ခုချင်းစီကို ID တပ်ဖို့

```python
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info("application_startup", app_name=settings.app_name, env=settings.app_env)
    yield
    logger.info("application_shutdown")
```

`lifespan` က app startup/shutdown event ပါ။ Django မှာ server စတက်ချိန် initialization logic ထည့်သလိုမျိုးပါ။

- `yield` မတိုင်ခင် code က startup မှာ run တယ်။
- `yield` ပြီးနောက် code က shutdown မှာ run တယ်။

```python
def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
```

`create_app()` က app factory pattern ပါ။ Django မှာ `get_wsgi_application()` / `get_asgi_application()` က app object ထုတ်သလိုမျိုး။

```python
app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)
```

FastAPI app တည်ဆောက်တာပါ။

- Swagger docs: `/api/v1/docs`
- ReDoc docs: `/api/v1/redoc`
- OpenAPI JSON: `/api/v1/openapi.json`

```python
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Middleware တွေထည့်တာပါ။ Django `MIDDLEWARE = [...]` နဲ့ ဆင်တူပါတယ်။

```python
app.include_router(api_router, prefix=settings.api_v1_prefix)
```

ဒီ line ကြောင့် `api_router` ထဲက route အားလုံးဟာ `/api/v1` prefix နဲ့စပါတယ်။

```python
app = create_app()
```

Uvicorn က `app.main:app` ဆိုပြီး ဒီ object ကို run ပါတယ်။

## `app/core/config.py`

ဒီ file က Django `settings.py` နဲ့အနီးဆုံးပါ။

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
```

`BaseSettings` က `.env` ထဲက values တွေကို class attributes အဖြစ် ဖတ်ပေးပါတယ်။

```python
app_name: str = "FastAPI Project"
app_env: Literal["development", "staging", "production"] = "development"
debug: bool = False
api_v1_prefix: str = "/api/v1"
```

App config တွေပါ။ Django မှာ `DEBUG`, project name, URL prefix config ထားသလိုပါ။

```python
database_url: str = Field(default="sqlite+aiosqlite:///./sql_app.db")
```k

Database connection string ပါ။ ဒီ project က async SQLite driver `aiosqlite` သုံးထားပါတယ်။

```python
secret_key: str = Field(default="...")
algorithm: str = "HS256"
access_token_expire_minutes: int = 30
```

JWT token ထုတ်ဖို့ security settings တွေပါ။

```python
@property
def cors_origin_list(self) -> list[str]:
    return [origins.strip() for origins in self.cors_origins.split(",") if origins.strip()]
```

`.env` ထဲက comma-separated CORS origins string ကို list ပြောင်းပေးတာပါ။

```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

Settings object ကို cache လုပ်ထားတာပါ။ Request တိုင်း `.env` ပြန်ဖတ်မနေအောင်ပါ။

## `app/core/security.py`

Password hashing နဲ့ JWT token logic တွေပါ။

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
```

Login ဝင်တဲ့အခါ user ရိုက်ထည့်တဲ့ password နဲ့ DB ထဲက hashed password ကို တိုက်စစ်တာပါ။

```python
def get_password_hash(password: str) -> str:
    pwbytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwbytes, salt)
    return hashed_password.decode("utf-8")
```

Register လုပ်တဲ့အခါ plain password ကို DB ထဲမသိမ်းဘဲ bcrypt hash ပြောင်းပါတယ်။

```python
def create_access_token(subject: str | UUID, expires_delta: timedelta = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
```

JWT access token ထုတ်တာပါ။

- `sub`: token ပိုင်ရှင် user id
- `exp`: token expire time

```python
def decode_access_token(token: str) -> str | None:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    subject = payload.get("sub")
    return subject
```

Bearer token ထဲက user id ကို ပြန်ဖတ်တာပါ။ Invalid token ဖြစ်ရင် `None` ပြန်ပါတယ်။

## `app/core/exceptions.py`

Custom HTTP exceptions တွေပါ။

```python
class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)
```

FastAPI ရဲ့ `HTTPException` ကို base class အဖြစ် extend လုပ်ထားတာပါ။

```python
class NotFoundException(AppException):
    ...
```

`404 Not Found` ထုတ်ဖို့။

```python
class UnauthorizedException(AppException):
    ...
```

`401 Unauthorized` ထုတ်ဖို့။

```python
class ConflictException(AppException):
    ...
```

`409 Conflict` ထုတ်ဖို့။ ဥပမာ email duplicate ဖြစ်တဲ့အခါ။

## `app/core/logging.py`

Structured logging setup ပါ။

```python
log_level = logging.DEBUG if settings.debug else logging.INFO
```

Debug mode ဖြစ်ရင် verbose log ထုတ်တယ်။

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        ...
    ],
)
```

Request ID, log level, timestamp တွေပါအောင် log format သတ်မှတ်ထားတာပါ။

## `app/middleware/request_id.py`

Request တစ်ခုချင်းစီကို unique ID တပ်ပေးတဲ့ middleware ပါ။

```python
request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
```

Client က `X-Request-ID` ပို့ထားရင် အဲဒါသုံးတယ်။ မပို့ထားရင် UUID အသစ်ထုတ်တယ်။

```python
structlog.contextvars.bind_contextvars(request_id=request_id)
```

Log တွေထဲ request id ပါအောင် bind လုပ်တာပါ။

```python
response = await call_next(request)
response.headers["X-Request-ID"] = request_id
return response
```

Request ကို next handler ဆီပို့ပြီး response header ထဲ request id ပြန်ထည့်ပေးပါတယ်။

## `app/db/base.py`

SQLAlchemy ORM base class နဲ့ timestamp mixin ပါ။

```python
class Base(DeclarativeBase):
    pass
```

Model class အားလုံး inherit လုပ်မယ့် base class ပါ။ Django model တွေ `models.Model` inherit လုပ်သလိုပါ။

```python
class TimestampMixin:
    created_at = mapped_column(...)
    updated_at = mapped_column(...)
```

Model အများကြီးမှာ `created_at`, `updated_at` ထပ်ရေးစရာမလိုအောင် mixin ထုတ်ထားတာပါ။

## `app/db/session.py`

Database engine/session setup ပါ။

```python
engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
    pool_pre_ping=True,
)
```

Async SQLAlchemy engine တည်ဆောက်တာပါ။

- `database_url`: DB connection string
- `echo=True`: SQL query logs ထုတ်တယ်
- `pool_pre_ping=True`: DB connection alive ဖြစ်/မဖြစ် စစ်တယ်

```python
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
```

Request တစ်ခုချင်းစီအတွက် session factory ပါ။

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

FastAPI dependency ပါ။ Endpoint ထဲမှာ DB session လိုရင် ဒီ function က session ပေးပါတယ်။

- Error မရှိရင် `commit()`
- Error ဖြစ်ရင် `rollback()`

Django မှာ ORM transaction ကို framework က handle လုပ်ပေးသလို ဒီမှာ dependency က handle လုပ်ထားတာပါ။

## `app/models/user.py`

SQLAlchemy model ပါ။ Django `models.py` နဲ့ တူပါတယ်။

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
```

`users` table ကို represent လုပ်တဲ့ Python class ပါ။

```python
id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
```

UUID primary key သုံးထားပါတယ်။ Django မှာ:

```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4)
```

နဲ့ဆင်တူပါတယ်။

```python
username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
```

`username`, `email` ကို unique/index ထားထားတယ်။

```python
hashed_password: Mapped[str] = mapped_column(String, nullable=False)
```

Password hash ကိုသိမ်းတဲ့ column ပါ။ Plain password မသိမ်းပါ။

```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

Django user model ရဲ့ `is_active`, `is_superuser` နဲ့ အဓိပ္ပါယ်တူပါတယ်။

မှတ်ချက်: ဒီ model မှာ `TimestampMixin` က `created_at` ပေးထားပြီး model ထဲမှာလည်း `created_at` ပြန်ရေးထားပါတယ်။ အလုပ်လုပ်နိုင်ပေမယ့် design အနေနဲ့ တစ်နေရာတည်းမှာထားတာ ပိုရှင်းပါတယ်။

## `app/models/__init__.py`

```python
from app.models.user import User

__all__ = ["User"]
```

Model တွေကို package level ကနေ import လုပ်လို့ရအောင် export လုပ်ထားတာပါ။ Alembic က model metadata သိဖို့လည်း အသုံးဝင်ပါတယ်။

## `app/schemas/common.py`

Pydantic common schemas တွေပါ။ DRF serializer base/response serializer တွေနဲ့ဆင်တူပါတယ်။

```python
class MessageResponse(BaseModel):
    message: str
```

Simple response format:

```json
{"message": "User deleted successfully"}
```

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
```

Pagination response format ပါ။

```python
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

SQLAlchemy model object ကနေ Pydantic schema ပြောင်းလို့ရအောင်ပါ။

ဥပမာ:

```python
UserRead.model_validate(user)
```

## `app/schemas/user.py`

User request/response schemas တွေပါ။

```python
class UserBase(ORMBase):
    email: EmailStr
    full_name: str | None = None
    username: str
    phone: str
    is_active: bool = True
    is_superuser: bool = False
```

User schema တွေမှာ share လုပ်မယ့် fields တွေပါ။

```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
```

Register request body ပါ။

```python
@model_validator(mode="after")
def verify_password_match(self) -> "UserCreate":
    if self.password != self.confirm_password:
        raise ValueError("Passwords do not match")
    return self
```

`password` နဲ့ `confirm_password` တူမတူ validation လုပ်တာပါ။

```python
class UserUpdate(ORMBase):
    email: EmailStr | None = None
    full_name: str | None = None
    username: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
```

Update request body ပါ။ Field အားလုံး optional ဖြစ်လို့ PATCH endpoint နဲ့သင့်တော်ပါတယ်။

```python
class UserRead(UserBase):
    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
```

API response ထဲပြန်ပေးမယ့် user shape ပါ။ Password မပါပါ။

```python
class UserInDB(UserRead):
    hashed_password: str
```

Internal DB representation အတွက်ပါ။ Public API response မဟုတ်ပါ။

## `app/schemas/token.py`

```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

Login success response ပါ။

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

```python
class TokenPayload(BaseModel):
    sub: str | None = None
```

JWT token ထဲက payload shape ကို represent လုပ်ဖို့ပါ။

## `app/repositories/user_repository.py`

Repository layer က DB query တွေကို endpoint/service ထဲမရောအောင် ခွဲထားတာပါ။ Django မှာ custom manager/queryset ဒါမှမဟုတ် service ထဲက ORM query logic နဲ့ဆင်တူပါတယ်။

```python
class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
```

Repository object ဆောက်တဲ့အခါ DB session လက်ခံပါတယ်။

```python
async def get_by_id(self, user_id: UUID) -> User | None:
    result = await self.db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

ID နဲ့ user ရှာတာပါ။ Django မှာ:

```python
User.objects.filter(id=user_id).first()
```

နဲ့တူပါတယ်။

```python
async def get_by_email(self, email: str) -> User | None:
    result = await self.db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

Email နဲ့ user ရှာတာပါ။

```python
async def list_users(self, *, skip: int = 0, limit: int = 2) -> tuple[list[User], int]:
    count_result = await self.db.execute(select(func.count()).select_from(User))
    total = count_result.scalar()
```

Total user count ယူတာပါ။

```python
result = await self.db.execute(
    select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
)
users = result.scalars().all()
```

Pagination အတွက် users list ယူတာပါ။ Django မှာ:

```python
User.objects.order_by("-created_at")[skip:skip + limit]
```

နဲ့ဆင်တူပါတယ်။

```python
async def create(...):
    user = User(...)
    self.db.add(user)
    await self.db.commit()
    await self.db.refresh(user)
    return user
```

User အသစ် create လုပ်တာပါ။

- `add`: session ထဲထည့်
- `commit`: DB ထဲသိမ်း
- `refresh`: DB-generated values ပြန်ယူ

```python
async def update(self, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True, exclude={"password", "confirm_password"})
    for fields, value in update_data.items():
        setattr(user, fields, value)
    await self.db.flush()
    await self.db.refresh(user)
    return user
```

PATCH update logic ပါ။

- `exclude_unset=True`: request ထဲမပါလာတဲ့ fields တွေ မပြောင်း
- `setattr`: model object ပေါ်မှာ value ပြောင်း
- `flush`: SQL ကို DB transaction ထဲပို့
- commit ကို `get_db()` dependency က နောက်ဆုံးလုပ်ပေးမယ်

```python
async def delete(self, user: User) -> None:
    await self.db.delete(user)
    await self.db.flush()
```

User delete လုပ်တာပါ။

```python
async def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
    query = select(User.id).where(User.email == email)
    if exclude_id is not None:
        query = query.where(User.id != exclude_id)
    result = await self.db.execute(query)
    return result.scalar_one_or_none() is not None
```

Email duplicate ရှိ/မရှိစစ်တာပါ။ Update လုပ်တဲ့အခါ current user id ကို exclude လုပ်လို့ရအောင် `exclude_id` ထည့်ထားတယ်။

မှတ်ချက်: ဒီ project မှာ user id က UUID ဖြစ်လို့ `exclude_id: int | None` ထက် `exclude_id: UUID | None` က ပိုမှန်ပါတယ်။

## `app/services/user_service.py`

Business logic layer ပါ။ Endpoint က HTTP အပိုင်းပဲကိုင်ပြီး အလုပ်လုပ်တဲ့ logic တွေကို service ထဲထားပါတယ်။

```python
class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)
```

Service တစ်ခုဆောက်တဲ့အခါ repository တစ်ခုဆောက်ထားပါတယ်။

```python
async def register(self, data: UserCreate) -> UserRead:
    if await self.repo.email_exists(data.email):
        raise ConflictException("Email already exists")
```

Register မလုပ်ခင် email duplicate စစ်ပါတယ်။

```python
user = await self.repo.create(
    email=data.email,
    username=data.username,
    full_name=data.full_name,
    phone=data.phone,
    hashed_password=get_password_hash(data.password),
    is_superuser=data.is_superuser,
    is_active=data.is_active,
)
```

Password ကို hash ပြောင်းပြီး repository ကို create ခိုင်းပါတယ်။

```python
return UserRead.model_validate(user)
```

SQLAlchemy user object ကို API response schema ပြောင်းတာပါ။

```python
async def authenticate(self, email: str, password: str) -> Token:
    user = await self.repo.get_by_email(email)
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Incorrect email or password")
```

Login logic ပါ။ Email မရှိရင် ဒါမှမဟုတ် password မမှန်ရင် 401 error ပစ်ပါတယ်။

```python
if not user.is_active:
    raise UnauthorizedException("Inactive user")
```

Inactive user ကို login မဝင်ခိုင်းပါ။

```python
token = create_access_token(subject=user.id)
return Token(access_token=token)
```

JWT token ထုတ်ပြီး response ပြန်ပါတယ်။

```python
async def list_users(self, page: int = 1, size: int = 20) -> PaginatedResponse[UserRead]:
    skip = (page - 1) * size
    users, total = await self.repo.list_users(skip=skip, limit=size)
```

Page number ကို DB offset အဖြစ်ပြောင်းပါတယ်။

```python
pages=math.ceil(total / size) if total else 0
```

Total pages တွက်တာပါ။

```python
async def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead:
    user = await self.repo.get_by_id(user_id)
    if user is None:
        raise NotFoundException("User")
```

Update မလုပ်ခင် user ရှိ/မရှိစစ်ပါတယ်။

```python
if data.email and await self.repo.email_exists(data.email, exclude_id=user_id):
    raise ConflictException("Email already in use")
```

Email ပြောင်းမယ်ဆို duplicate မဖြစ်အောင် စစ်ပါတယ်။

```python
if data.password:
    user.hashed_password = get_password_hash(data.password)
```

မှတ်ချက်: `UserUpdate` schema ထဲမှာ `password` field မပါသေးလို့ ဒီ line က လက်ရှိ code အတိုင်းဆို အလုပ်မလုပ်နိုင်ပါ။ Password update လုပ်ချင်ရင် `UserUpdate` ထဲ `password` ထည့်ဖို့လိုပါတယ်။

## `app/api/deps.py`

FastAPI dependency injection တွေ စုထားတဲ့ file ပါ။ Django/DRF မှာ authentication class, permission class, request helpers တွေလိုမျိုးပါ။

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
```

Swagger UI မှာ Bearer token auth သုံးဖို့ setup လုပ်တာပါ။ Request header ထဲက:

```http
Authorization: Bearer <token>
```

ကိုဖတ်ပါတယ်။

```python
class LoginPayload(BaseModel):
    email: str
    password: str
```

Login request body shape ပါ။

```python
async def get_login_credentials(request: Request) -> LoginPayload:
```

Login request ကို JSON သို့မဟုတ် form data နှစ်မျိုးလုံး accept လုပ်ဖို့ custom dependency ပါ။

```python
body = await request.json()
return LoginPayload(**body)
```

JSON body ဖတ်ပါတယ်။

```python
form = await request.form()
email = form.get("email")
password = form.get("password")
```

JSON မဟုတ်ရင် form data ဖတ်ပါတယ်။

```python
DbSession = Annotated[AsyncSession, Depends(get_db)]
```

DB session dependency ကို type alias လုပ်ထားတာပါ။ Endpoint/service dependency တွေမှာ သုံးရလွယ်အောင်ပါ။

```python
def get_user_service(db: DbSession) -> UserService:
    return UserService(db)
```

DB session ကိုအသုံးပြုပြီး `UserService` object ထုတ်ပေးပါတယ်။

```python
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

Endpoint တွေထဲမှာ:

```python
service: UserServiceDep
```

လို့ရေးလိုက်တာနဲ့ FastAPI က service inject လုပ်ပေးပါတယ်။

```python
async def get_current_user(db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user_id = decode_access_token(token)
```

Bearer token ကို decode လုပ်ပြီး user id ထုတ်ပါတယ်။

```python
repo = UserRepository(db)
user = await repo.get_by_id(UUID(user_id))
```

Token ထဲက user id နဲ့ DB ထဲက user ကိုရှာပါတယ်။

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

Endpoint ထဲမှာ current user လိုရင်:

```python
current_user: CurrentUser
```

လို့သုံးနိုင်ပါတယ်။

```python
async def get_current_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise UnauthorizedException("Not enough permissions")
    return current_user
```

Superuser permission စစ်တာပါ။

## `app/api/v1/router.py`

Version 1 API routes တွေ စုပေးတဲ့ router ပါ။

```python
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

Final URLs:

```text
/api/v1/health
/api/v1/auth/register
/api/v1/auth/login
/api/v1/users/me
/api/v1/users
/api/v1/users/{user_id}
```

Django မှာ root `urls.py` က app urls တွေ include လုပ်သလိုပါ။

## `app/api/v1/endpoints/health.py`

```python
@router.get("/health", response_model=MessageResponse)
async def health_check() -> MessageResponse:
    settings = get_settings()
    return MessageResponse(message=f"{settings.app_name} is running")
```

Health check endpoint ပါ။ Server alive ဖြစ်/မဖြစ် စစ်ဖို့သုံးပါတယ်။

Response:

```json
{
  "message": "FastAPI Project is running"
}
```

## `app/api/v1/endpoints/auth.py`

Auth endpoints ပါ။

```python
@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserCreate, service: UserServiceDep) -> UserRead:
    return await service.register(data)
```

Register endpoint ပါ။

- Request body ကို `UserCreate` နဲ့ validate လုပ်တယ်။
- `UserServiceDep` က service object inject လုပ်တယ်။
- Actual logic ကို `service.register()` ထဲပို့တယ်။
- Response ကို `UserRead` shape နဲ့ပြန်တယ်။

```python
@router.post("/login", response_model=Token)
async def login(
    credentials: Annotated[LoginPayload, Depends(get_login_credentials)],
    service: UserServiceDep,
) -> Token:
    return await service.authenticate(credentials.email, credentials.password)
```

Login endpoint ပါ။

- `get_login_credentials` က request body/form data ဖတ်တယ်။
- `service.authenticate()` က email/password စစ်တယ်။
- Success ဖြစ်ရင် JWT token ပြန်တယ်။

## `app/api/v1/endpoints/users.py`

User management endpoints ပါ။

```python
@router.get("/me", response_model=UserRead)
async def get_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
```

Logged-in user ကိုပြန်ပေးတဲ့ endpoint ပါ။

`CurrentUser` dependency ကြောင့် token မရှိရင် 401 ထွက်မယ်။

```python
@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    _: CurrentSuperuser,
    service: UserServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[UserRead]:
    return await service.list_users(page=page, size=size)
```

Users list endpoint ပါ။

- `_ : CurrentSuperuser` ဆိုတာ current superuser ဖြစ်/မဖြစ် permission စစ်ဖို့ပါ။
- `_` variable name သုံးတာက value ကို မသုံးဘူးဆိုတဲ့ Python convention ပါ။
- `page` က 1 ထက်ငယ်လို့မရ။
- `size` က 1 မှ 100 ကြားပဲရ။

```python
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, _: CurrentSuperuser, service: UserServiceDep) -> UserRead:
    return await service.get_user(user_id)
```

Specific user detail endpoint ပါ။ Superuser only.

```python
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, data: UserUpdate, _: CurrentSuperuser, service: UserServiceDep) -> UserRead:
    return await service.update_user(user_id, data)
```

User update endpoint ပါ။ PATCH ဖြစ်လို့ partial update လုပ်နိုင်ပါတယ်။

```python
@router.delete("/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, _: CurrentSuperuser, service: UserServiceDep) -> MessageResponse:
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
```

User delete endpoint ပါ။ Delete ပြီး message response ပြန်ပါတယ်။

## Alembic

Alembic က SQLAlchemy project တွေအတွက် migration tool ပါ။ Django migration နဲ့တူတဲ့ role ဖြစ်ပါတယ်။

### `alembic/env.py`

```python
settings = get_settings()
config.set_main_option("sqlalchemy.url", str(settings.database_url))
```

Migration run တဲ့အခါ `.env` / settings ထဲက database URL ကိုသုံးပါတယ်။

```python
from app.models import User
target_metadata = Base.metadata
```

Model metadata ကို Alembic ကသိအောင် import လုပ်ထားပါတယ်။ Autogenerate migration လုပ်ဖို့လိုပါတယ်။

```python
async def run_async_migrations() -> None:
    connectable = create_async_engine(str(settings.database_url), poolclass=pool.NullPool)
```

ဒီ project က async DB engine သုံးထားလို့ migration ကို async engine နဲ့ run အောင်ရေးထားတာပါ။

### `alembic/versions/7d5a575c7654_create_user_table_with_uuid.py`

Initial migration file ပါ။

```python
def upgrade() -> None:
    op.create_table("users", ...)
```

`upgrade()` က migration apply လုပ်တဲ့အခါ run ပါတယ်။ `users` table create လုပ်ပါတယ်။

```python
def downgrade() -> None:
    op.drop_table("users")
```

`downgrade()` က migration rollback လုပ်တဲ့အခါ run ပါတယ်။

## Main API Flows

### Register Flow

```text
POST /api/v1/auth/register
  -> auth.register()
  -> UserService.register()
  -> UserRepository.email_exists()
  -> get_password_hash()
  -> UserRepository.create()
  -> UserRead response
```

Request example:

```json
{
  "email": "admin@example.com",
  "username": "admin",
  "full_name": "Admin User",
  "phone": "09123456789",
  "password": "password123",
  "confirm_password": "password123",
  "is_superuser": true,
  "is_active": true
}
```

### Login Flow

```text
POST /api/v1/auth/login
  -> get_login_credentials()
  -> UserService.authenticate()
  -> UserRepository.get_by_email()
  -> verify_password()
  -> create_access_token()
  -> Token response
```

Response example:

```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

### Current User Flow

```text
GET /api/v1/users/me
  -> CurrentUser dependency
  -> oauth2_scheme reads Bearer token
  -> decode_access_token()
  -> UserRepository.get_by_id()
  -> UserRead response
```

Header example:

```http
Authorization: Bearer jwt-token-here
```

### Superuser List Users Flow

```text
GET /api/v1/users?page=1&size=10
  -> CurrentSuperuser dependency
  -> UserService.list_users()
  -> UserRepository.list_users()
  -> PaginatedResponse[UserRead]
```

## FastAPI Concepts You Need to Know

### `async def`

ဒီ project က async FastAPI + async SQLAlchemy သုံးထားပါတယ်။ DB query တွေမှာ `await` သုံးရပါတယ်။

```python
user = await self.repo.get_by_email(email)
```

Django classic ORM က sync ဖြစ်ပေမယ့် ဒီ project မှာ DB calls တွေ async ဖြစ်ပါတယ်။

### `Depends`

FastAPI dependency injection ပါ။

```python
service: UserServiceDep
```

ဒီလိုရေးလိုက်ရင် FastAPI က service object ကို endpoint ထဲ inject လုပ်ပေးပါတယ်။

### `response_model`

Endpoint response ကို ဘယ် schema နဲ့ပြန်မလဲ သတ်မှတ်တာပါ။

```python
@router.post("/register", response_model=UserRead)
```

DRF serializer response နဲ့တူပါတယ်။

### Pydantic Schemas

Request body validation, response serialization နှစ်ခုလုံးကို Pydantic က handle လုပ်ပါတယ်။

```python
async def register(data: UserCreate)
```

Request body မမှန်ရင် FastAPI က automatic 422 validation error ပြန်ပါတယ်။

## Things to Improve Later

ဒီ project က learning project အနေနဲ့ကောင်းပါတယ်။ နောက်တစ်ဆင့် improve လုပ်ချင်ရင်:

1. `UserUpdate` ထဲ password update fields ထည့်မလား၊ service ထဲက password update logic ဖယ်မလား ဆုံးဖြတ်ပါ။
2. `email_exists(exclude_id: int | None)` ကို `UUID | None` ပြောင်းပါ။
3. `User` model ထဲက duplicate `created_at` definition ကိုရှင်းပါ။
4. `register` endpoint မှာ public user က `is_superuser=True` ပို့နိုင်တာကို production မှာမခွင့်ပြုသင့်ပါ။
5. Tests folder ထဲ unit/integration tests ထည့်ပါ။
6. `.env` ထဲက real secret key ကို git ထဲမထည့်ပါ။

