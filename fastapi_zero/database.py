from sqlalchemy import create_engine
from fastapi_zero.settings import Settings
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(Settings().DATABASE_URL)  # CONEXÃO COM O BANCO DE DADOS
session = Session(engine)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Usamos o Yield pra nao parar a sessão, pois com o return a função quebra a execução e não é isso que queremos
        yield session
