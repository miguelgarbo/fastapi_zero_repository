from fastapi import FastAPI, HTTPException, Depends
from http import HTTPStatus
import fastapi.responses as response
import fastapi_zero.schemas as schema
from fastapi_zero.models import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi_zero.database import get_session
from fastapi_zero.security import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI(title='API To Do')

@app.post('/token', response_model=schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username)) 

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=schema.Message,
    response_class=response.JSONResponse,
)
def read_root():
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
        password= get_password_hash(user.password),
       )
        
    session.add(db_user)
    session.commit()
    session.refresh
    
    return db_user
   

@app.get('/users/', response_model=schema.UserList, status_code=HTTPStatus.OK)
#Esse limit e offset é pra definir que na hora que vier a lista de users ele separe esse retorno por paginas
#São os query params
def read_users(limit:int =10,offset:int =0,
               session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    
    users = session.scalars(
        select(User).limit(limit).offset(offset)
    )
    
    return {'users': users}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic)
def update_user(user_id: int, userNewInfo: schema.UserSchema, 
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
        
    if(current_user.id != user_id):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Sem Permissão'
        )
        
    
    try:
            current_user.username = userNewInfo.username
            current_user.email = userNewInfo.email
            current_user.password = get_password_hash(userNewInfo.password)
            #Manda Pro banco
            session.commit()
            #Atualiza o usuario atualizado para recebermos
            session.refresh(current_user)
            
            return current_user;
    except IntegrityError:
        raise HTTPException(detail="Username Ou Email Já exitem no Banco de Dados", status_code= HTTPStatus.CONFLICT)

    

@app.delete(                                                                   
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=str,
)
def delete_user(user_id: int, 
                session: Session = Depends(get_session), 
                current_user: User = Depends(get_current_user)):
   
    if current_user.id != user_id:
        raise HTTPException( status_code=HTTPStatus.FORBIDDEN, detail='Sem Permissão ')
    
        
    session.delete(current_user)
    session.commit()
    
    return f'Usuário {current_user.username} Deletado Com Sucesso'
    

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
        raise HTTPException(detail="Usuário Não Encontrado",status_code=HTTPStatus.NOT_FOUND)

    

    return db_user

        
    
   
