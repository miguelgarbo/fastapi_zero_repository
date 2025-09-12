from fastapi import FastAPI, HTTPException
from http import HTTPStatus
import fastapi.responses as response
import fastapi_zero.schemas as schema
from fastapi_zero.models import User

app = FastAPI(title='API To Do')


dataBase = []


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=schema.Message,
    response_class=response.JSONResponse,
)
def read_root():
    # return {'message': "123"}
    return schema.Message(message='Olá Mundo!')


@app.get(
    '/htmlEndPoint',
    status_code=HTTPStatus.OK,
    response_class=response.HTMLResponse,
)
def get_html():
    return """ 
        <html>
        <h1> Olá Mundo</h1>
        <input type="text" value="Valor">
        </html>
"""


@app.post(
    '/users/', response_model=schema.UserPublic, status_code=HTTPStatus.CREATED
)
# Se transforma pro objeto userSchema
# Se Não for valido ele dá erro sozinho
def create_user(user: schema.UserSchema):
    # O Model Dump pega todos os campos de User e tranforma o modelo em dicionario
    # Esse '**' cria chave e valor de todos os campos, passando os valores para os parametros
    
    from sqlalchemy import create_engine, select
    from fastapi_zero.settings import Settings
    
    from sqlalchemy.orm import Session
    
    engine = create_engine(Settings().DATABASE_URL) #CONEXÃO COM O BANCO DE DADOS
    session = Session(engine)
    
    #SCALAR, retorna User ou None
    db_users = session.scalar(
        select(User).where(User.username == user.username | User.email == user.email)
    )
    
    # if db_users: :
    #     ...
        
   

@app.get('/users/', response_model=schema.UserList, status_code=HTTPStatus.OK)
def read_users():
    return {'users': dataBase}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic,
)
def update_user(user_id: int, userNewInfo: schema.UserSchema):
    if user_id < 1 or user_id > len(dataBase):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário Não Encontrado'
        )

    user_selected = schema.UserDB(**userNewInfo.model_dump(), id=user_id)
    dataBase[user_id - 1] = user_selected

    return user_selected


@app.delete(                                                                   
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic,
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(dataBase):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário Não Encontrado'
        )

    return dataBase.pop(user_id - 1)

@app.get(                                                                   
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic,
)
def read_user(user_id: int):
    if user_id < 1 or user_id > len(dataBase):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário Não Encontrado'
        )

    
    return dataBase[user_id - 1]
