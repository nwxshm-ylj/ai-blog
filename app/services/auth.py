from __future__ import annotations

import uuid
from dataclasses import dataclass

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.users import UserRepository

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SESSION_USER_ID_KEY = "user_id"
LOCAL_DEV_ADMIN_EMAIL = "admin@example.com"
LOCAL_DEV_ADMIN_USERNAME = "admin"
LOCAL_DEV_ADMIN_PASSWORD = "admin123"


@dataclass(frozen=True)
class LoginResult:
    user: User | None
    error: str | None = None


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)


async def authenticate_admin_user(
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
