from __future__ import annotations

import uuid
from dataclasses import dataclass
from re import fullmatch

import bcrypt as _bcrypt_backend
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

PASSWORD_MAX_BYTES = 72

if not hasattr(_bcrypt_backend, "__about__"):
    _bcrypt_backend.__about__ = type(  # type: ignore[attr-defined]
        "_About",
        (),
        {"__version__": getattr(_bcrypt_backend, "__version__", "unknown")},
    )()

    _bcrypt_hashpw = _bcrypt_backend.hashpw

    def _passlib_compatible_hashpw(password: bytes, salt: bytes) -> bytes:
        return _bcrypt_hashpw(password[:PASSWORD_MAX_BYTES], salt)

    _bcrypt_backend.hashpw = _passlib_compatible_hashpw

from passlib.context import CryptContext

from app.models.user import User
from app.repositories.users import UserRepository

PASSWORD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=True,
)

SESSION_USER_ID_KEY = "user_id"
SESSION_USERNAME_KEY = "username"
SESSION_IS_ADMIN_KEY = "is_admin"
LOCAL_DEV_ADMIN_EMAIL = "admin@example.com"
LOCAL_DEV_ADMIN_USERNAME = "admin"
LOCAL_DEV_ADMIN_PASSWORD = "admin123"


@dataclass(frozen=True)
class LoginResult:
    user: User | None
    error: str | None = None


@dataclass(frozen=True)
class RegistrationData:
    email: str
    username: str
    password: str
    password_confirm: str


@dataclass(frozen=True)
class RegistrationResult:
    user: User | None
    errors: list[str]


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise ValueError("Password must be 72 bytes or fewer.")
    return PASSWORD_CONTEXT.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        return False
    try:
        return PASSWORD_CONTEXT.verify(password, hashed_password)
    except ValueError:
        return False


async def register_public_user(
    session: AsyncSession,
    data: RegistrationData,
) -> RegistrationResult:
    email = data.email.strip().lower()
    username = data.username.strip()
    password = data.password
    errors = await _validate_registration(session, email, username, password, data.password_confirm)
    if errors:
        return RegistrationResult(user=None, errors=errors)

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        is_admin=False,
    )
    try:
        await UserRepository(session).add(user)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return RegistrationResult(
            user=None,
            errors=["An account with this email or username already exists."],
        )
    return RegistrationResult(user=user, errors=[])


async def authenticate_user(
    session: AsyncSession,
    identifier: str,
    password: str,
) -> LoginResult:
    normalized_identifier = identifier.strip()
    if not normalized_identifier or not password:
        return LoginResult(user=None, error="Email or username and password are required.")

    repository = UserRepository(session)
    user = await repository.get_by_email_or_username(normalized_identifier)
    if user is None or not verify_password(password, user.hashed_password):
        return LoginResult(user=None, error="Invalid email, username, or password.")

    return LoginResult(user=user)


async def authenticate_admin_user(
    session: AsyncSession,
    identifier: str,
    password: str,
) -> LoginResult:
    result = await authenticate_user(session, identifier, password)
    if result.user is None:
        return result
    user = result.user
    if not user.is_admin:
        return LoginResult(user=None, error="This account cannot access the admin area.")

    return LoginResult(user=user)


async def get_user_by_session_id(session: AsyncSession, user_id: str | None) -> User | None:
    if not user_id:
        return None

    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError:
        return None

    return await UserRepository(session).get(parsed_user_id)


async def create_local_development_admin(session: AsyncSession) -> User:
    repository = UserRepository(session)
    user = await repository.get_by_email_or_username(LOCAL_DEV_ADMIN_EMAIL)
    if user is None:
        user = User(
            email=LOCAL_DEV_ADMIN_EMAIL,
            username=LOCAL_DEV_ADMIN_USERNAME,
            hashed_password=hash_password(LOCAL_DEV_ADMIN_PASSWORD),
            is_admin=True,
        )
        await repository.add(user)
    else:
        user.email = LOCAL_DEV_ADMIN_EMAIL
        user.username = LOCAL_DEV_ADMIN_USERNAME
        user.hashed_password = hash_password(LOCAL_DEV_ADMIN_PASSWORD)
        user.is_admin = True

    await session.commit()
    return user


async def _validate_registration(
    session: AsyncSession,
    email: str,
    username: str,
    password: str,
    password_confirm: str,
) -> list[str]:
    errors: list[str] = []
    if not email:
        errors.append("Email is required.")
    elif "@" not in email or "." not in email.rsplit("@", maxsplit=1)[-1]:
        errors.append("Enter a valid email address.")

    if not username:
        errors.append("Username is required.")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    elif len(username) > 100:
        errors.append("Username must be 100 characters or fewer.")
    elif fullmatch(r"[A-Za-z0-9_-]+", username) is None:
        errors.append("Username can only use letters, numbers, underscores, and hyphens.")

    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    elif len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        errors.append("Password must be 72 bytes or fewer.")
    if password != password_confirm:
        errors.append("Password confirmation does not match.")

    if errors:
        return errors

    repository = UserRepository(session)
    if await repository.get_by_email(email) is not None:
        errors.append("An account with this email already exists.")
    if await repository.get_by_username(username) is not None:
        errors.append("An account with this username already exists.")
    return errors
