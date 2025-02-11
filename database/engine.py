from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import asyncio
from .schema.meta import Base 
from config import db_location

async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


engine = create_async_engine(f'sqlite+aiosqlite:///{db_location}')

# Create an async session factory
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

async_session = AsyncSession(engine, expire_on_commit=False)
asyncio.run(create_tables(engine))

# python -m database.engine
def main():

    print('create database')
    pass
    

if __name__ == "__main__":
    main()

