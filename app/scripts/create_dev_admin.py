from __future__ import annotations

import asyncio

from app.db.database import async_session_factory
from app.services.auth import (
    LOCAL_DEV_ADMIN_EMAIL,
    LOCAL_DEV_ADMIN_PASSWORD,
    LOCAL_DEV_ADMIN_USERNAME,
    create_local_development_admin,
)


async def main() -> None:
    async with async_session_factory() as session:
        await create_local_development_admin(session)

    print("Local development admin user is ready.")
    print("This helper is only for local development.")
    print(f"email: {LOCAL_DEV_ADMIN_EMAIL}")
    print(f"username: {LOCAL_DEV_ADMIN_USERNAME}")
    print(f"password: {LOCAL_DEV_ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
