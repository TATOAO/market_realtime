import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List

from sqlalchemy.sql import text
from utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import *
from .engine import engine, AsyncSessionFactory
from sqlalchemy.exc import IntegrityError

class AsyncDBManager:
    def __init__(self, session_factory=AsyncSessionFactory):
        self.session_factory = session_factory
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, Exception]:
        """
        An async context manager for providing an AsyncSession.
        Handles commit/rollback automatically.
        """
        session = self.session_factory()
        try:
            yield session
            await session.commit()  # Commits if everything is OK
        except Exception as e:
            await session.rollback()
            logger.error(f"Session rollback because of exception: {e}")
        finally:
            await session.close()

    async def init_db(self):
        """
        Initialize the database (e.g., create tables).
        This is optional if you manage migrations externally (e.g. Alembic).
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def execute_sql(self, sql: str) -> List[dict]:
        """
        Execute a raw SQL query and return the results as a list of dicts.
        """
        async with self.get_session() as session:
            result = await session.execute(text(sql))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]

class AsyncMarketDBManager(AsyncDBManager):

    pass



def main():
    pass

    
# python -m database.__init__
if __name__ == "__main__":
    main()

