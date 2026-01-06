import asyncio

from sqlmodel import Session

from app.core.db import engine, init_db
from app.core.logging_config import app_logger


async def init() -> None:
    with Session(engine) as session:
        await init_db(session)


async def main() -> None:
    app_logger.info('Creating initial data')
    await init()
    app_logger.info('Initial data created')


if __name__ == '__main__':
    asyncio.run(main())
