import factory.fuzzy
from fastapi.testclient import TestClient
from fastapi_zero.app import app
import pytest
# from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from fastapi_zero.settings import Settings

from fastapi_zero.database import get_session

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import pytest_asyncio

# Pegando o Registro das Tabelas
from fastapi_zero.models import table_registry, User, TodoState

from sqlalchemy import event

# Importando a Tabela
from fastapi_zero.models import User, Todo
import datetime
from contextlib import contextmanager
from fastapi_zero.security import get_password_hash

import factory
from faker import Faker

from testcontainers.postgres import PostgresContainer


# Como no app.py a gente usa o get_session() para acessar o banco e nos testes nós não podemos acessar o banco
# Nós iremos sobrescrever para ele pegar a session de teste, e não a do banco de dados real
# Reseta o banco de dados em memoria a cada test
@pytest.fixture
def client(session: AsyncSession):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    # Depois que a gambiarra for executada ele limpa tudo
    app.dependency_overrides.clear()

#esse scope session, signifca que essa fixture vai rodar uma vez  a cada execução de todos os testes, por padrão esse scope é function que seria a cada vez q essa função é chamada
@pytest.fixture(scope='session')
def engine():
        # Conexão com o Banco de dados , que é um container que sobe a cada execução de teste
     with PostgresContainer('postgres:17',driver='psycopg') as postgresDB:
        engine = create_async_engine(postgresDB.get_connection_url())
        yield engine

@pytest_asyncio.fixture
async def session(engine):    

        # Criação das tabelas
        #Tornando a criação de tabelas não assincronas
    async with engine.begin() as conn: 
         await conn.run_sync(table_registry.metadata.create_all) 

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
        


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = 'teste'

    user = UserFactory(
       
        password=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Cria um atributo apenas nesse escopo
    user.clean_password = password
    return user

@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    password = 'teste2'

    user = UserFactory(
       
        password=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Cria um atributo apenas nesse escopo
    user.clean_password = password
    return user


@contextmanager
def _mock_db_time(*, model:User, time=datetime.datetime(2025, 5, 20)):
    def fake_time_hook(mapper, connection, target):
        # Aqui validamos se esse objeto tem o atributo, created at
        if hasattr(target, 'created_at'):
            # Ou Seja Antes de Inserir eu dou o tempo
            target.created_at = time
            
        if hasattr(target, 'updated_at'):
            target.updated_at = time

        print(target)

    # Aqui é aonde antes de inserir algo na model ele vai pegar
    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)
    


# Resumindo, essa fixture está configurando e limpando um banco de dados de teste para cada teste que o solicita,
# assegurando que cada teste seja isolado e tenha seu próprio ambiente limpo para trabalhar.
@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def tokenGerado(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']

@pytest.fixture
def settings():
    return Settings();

#Criação de usuarios para testes
#Toda Vez que essa função for chamada ele cria um usuario novo
class UserFactory(factory.Factory):
    class Meta:
        model = User
        
    #Apenas os atributos não inits    
    username = factory.sequence(lambda n: f'test{n}')
    #Esse lazy é para esse campo ser avaliado tardiamente, por isso o nome lazy(preguiçoso)
    #No Nosso Caso vai ser util pq o email vai esperar o username para poder usar o nome do user no email
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}123#')
    
class TodoFactory(factory.Factory):
    class Meta:
        model = Todo
        
    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1 