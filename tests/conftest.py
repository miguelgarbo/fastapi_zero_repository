from fastapi.testclient import TestClient
from fastapi_zero.app import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

#Pegando o Registro das Tabelas
from fastapi_zero.models import table_registry



@pytest.fixture
def client():
    return TestClient(app)

# AQUI a gente cria a conexão com o banco de dados
@pytest.fixture
def session():
    #Conexão com o Banco de dados
    engine = create_engine('sqlite:///memory:')
    
    #Criação das tabelas
    table_registry.metadata.create_all(engine)
    
    #Aqui a sessão é aberta de troca entre o banco de dados e o codigo
    #Na sessão é onde as querys ao banco serão feitas
    with Session(engine) as session:
        #O Yield da a sessão pra nós usarmos no teste
        yield session
        
    #Depois de acabar a execução do códiogo que a gente queria, a gnt da um drop all
    #Mantendo assim bom para realizar testes, mantendo limpo a cada teste
    table_registry.metadata.drop_all(engine)
    
#Mentir a hora que o banco de dados persistir alguma coisa

from sqlalchemy import event
#Importando a Tabela
from fastapi_zero.models import User
import datetime
from contextlib import contextmanager


@contextmanager
def _mock_db_time(*,model=User, time=datetime.datetime(2025,5,20)):
    
    def fake_time_hook(mapper, connection, target):
        #Aqui validamos se esse objeto tem o atributo, created at
        if hasattr(target, 'created_at'):
            
            #Ou Seja Antes de Inserir eu dou o tempo
            target.created_at = time
            
        
        print(target)
        
    # Aqui é aonde antes de inserir algo na model ele vai pegar
    event.listen(User, 'before_insert', fake_time_hook)
    
    yield time 
    
    event.remove(User, 'before_insert', fake_time_hook)
    
#Resumindo, essa fixture está configurando e limpando um banco de dados de teste para cada teste que o solicita,
#assegurando que cada teste seja isolado e tenha seu próprio ambiente limpo para trabalhar.    
@pytest.fixture
def mock_db_time():
    return _mock_db_time