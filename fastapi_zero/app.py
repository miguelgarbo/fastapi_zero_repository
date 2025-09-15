from fastapi import FastAPI, HTTPException, Depends
from http import HTTPStatus
import fastapi.responses as response
import fastapi_zero.schemas as schema
from fastapi_zero.models import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi_zero.database import get_session



app = FastAPI(title='API To Do')


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
def create_user(user: schema.UserSchema, session = Depends(get_session)):
    
    #SCALAR, retorna um User ou None
    #Aqui ele retorna os iguais dai no if ele quebra com um erro
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if(db_user.username == user.username):
            raise HTTPException(detail="Esse UserName Já Existe no Banco",status_code=HTTPStatus.CONFLICT)
        elif(db_user.email == user.email):
            raise HTTPException(detail="Esse Email Já Existe No Banco", status_code=HTTPStatus.CONFLICT)
        
    
    db_user = User(
        username= user.username,
        email= user.email,
        password= user.password,
       )
        
    session.add(db_user)
    session.commit()
    session.refresh
    
    return db_user
   

@app.get('/users/', response_model=schema.UserList, status_code=HTTPStatus.OK)
#Esse limit e offset é pra definir que na hora que vier a lista de users ele separe esse retorno por paginas
#São os query params
def read_users(limit:int =10,offset:int =0,session: Session = Depends(get_session)):
    
    users = session.scalars(
        select(User).limit(limit).offset(offset)
    )
    
    return {'users': users}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic,
)
def update_user(user_id: int, userNewInfo: schema.UserSchema, session: Session = Depends(get_session)):
   user_db = session.scalar(
       select(User).where(User.id == user_id)
   )
   
   if not user_db:
       raise HTTPException(detail="Esse Usuário Não Existe", status_code=HTTPStatus.NOT_FOUND)
   
   try:
        user_db.username = userNewInfo.username
        user_db.email = userNewInfo.email
        user_db.password = userNewInfo.password
        #Manda Pro banco
        session.commit()
        #Atualiza o usuario atualizado para recebermos
        session.refresh(user_db)
        
        return user_db;
   except IntegrityError:
       raise HTTPException(detail="Username Ou Email Já exitem no Banco de Dados", status_code= HTTPStatus.CONFLICT)

    

@app.delete(                                                                   
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=str,
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(
        
        select(User).where(User.id == user_id)
    )
    
    #Se Retornar None
    if not user_db:
        raise HTTPException(detail="Esse Usuário Não Existe", status_code= HTTPStatus.NOT_FOUND)
    
        
    session.delete(user_db)
    session.commit()
    
    return f'Usuário {user_db.username} Deletado Com Sucesso'
    

@app.get(                                                                   
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic,
)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(
        
        select(User).where(User.id == user_id)
    )
    
    if not db_user:
        raise HTTPException("Usuário Não Encontrado")
    

    return db_user

        
    
   
