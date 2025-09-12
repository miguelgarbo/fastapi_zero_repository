from fastapi_zero.models import User
from sqlalchemy import select
from dataclasses import asdict
from datetime import datetime

def test_create_user(session, mock_db_time):
    with mock_db_time(model=User, time=datetime.now()) as time:
        new_user = User(username='test', email='test@gmail.com', password='secret')

    session.add(new_user) #Adicionando User Na Sessão
   
    session.commit()  #Esse Commit é pra afirmar nossas operações pro banco de dados de verdade
    
    #Aqui é aonde eu capturo o resultado da requisição , vai me retornar e escalar
    #Tudo que voltat é transformado em objeto python
    user = session.scalar(
        #Seleciona la na tabela de users select from users
        #depois adicionamos o where para filtrar
        select(User).where(User.username =='test')
    )
    
    #Asdict tranforma o data class em dicionario
    assert asdict(user) == {
        'id':1,
        'username':'test',
        'email':'test@gmail.com',
        'password': 'secret',
        'createdAt': time,
        'updatedAt': time
    }