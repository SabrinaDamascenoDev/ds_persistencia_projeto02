import sqlite3
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event, Engine
from dotenv import load_dotenv
import logging
import ssl
import os

load_dotenv()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

DATABASE_URL = os.getenv("DATABASE_URL")

# ----- SSL SOMENTE PARA POSTGRES -----
if DATABASE_URL.startswith("postgresql"):
    ssl_ctx = ssl.create_default_context()
    connect_args = {"ssl": ssl_ctx}
else:
    connect_args = {}  # SQLite não usa SSL

# ----- ENGINE CORRETO -----
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args=connect_args
)

# ----- SESSIONMAKER CORRETO -----
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ----- DEPENDENCY DO FASTAPI -----
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# ----- PRAGMA DO SQLITE -----
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
