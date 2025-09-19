from fastapi_zero.models import User
from sqlalchemy import create_engine, select
from fastapi_zero.settings import Settings
from sqlalchemy.orm import Session


engine = create_engine(Settings().DATABASE_URL)  # CONEXÃO COM O BANCO DE DADOS
session = Session(engine)


def get_session():
    with Session(engine) as session:
        # Usamos o Yield pra nao parar a sessão, pois com o return a função quebra a execução e não é isso que queremos
        yield session
