from fastapi import HTTPException, Depends, APIRouter, Query
from http import HTTPStatus
import fastapi_zero.schemas as schema
from fastapi_zero.models import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi_zero.database import get_session
from fastapi_zero.security import get_password_hash, get_current_user
from typing import Annotated

router = APIRouter(prefix='/users', tags=['users'])

SessionDB = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterUsers = Annotated[schema.FilterPage, Query()]


@router.post(
    '/', response_model=schema.UserPublic, status_code=HTTPStatus.CREATED
)
# Se transforma pro objeto userSchema
# Se Não for valido ele dá erro sozinho
def create_user(user: schema.UserSchema, session: SessionDB):
    # SCALAR, retorna um User ou None
    # Aqui ele retorna os iguais dai no if ele quebra com um erro
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                detail='Esse UserName Já Existe no Banco',
                status_code=HTTPStatus.CONFLICT,
            )
        elif db_user.email == user.email:
            raise HTTPException(
                detail='Esse Email Já Existe No Banco',
                status_code=HTTPStatus.CONFLICT,
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh

    return db_user


@router.get('/', response_model=schema.UserList, status_code=HTTPStatus.OK)
# Esse limit e offset é pra definir que na hora que vier a lista de users ele separe esse retorno por paginas
# São os query params
def read_users(
    current_user: CurrentUser,
    session: SessionDB,
    filter_page: FilterUsers
):
    users = session.scalars(select(User).limit(filter_page.limit).offset(filter_page.offset))

    return {'users': users}


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=schema.UserPublic
)
def update_user(
    user_id: int,
    userNewInfo: schema.UserSchema,
    session: SessionDB,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Sem Permissão'
        )

    try:
        current_user.username = userNewInfo.username
        current_user.email = userNewInfo.email
        current_user.password = get_password_hash(userNewInfo.password)
        # Manda Pro banco
        session.commit()
        # Atualiza o usuario atualizado para recebermos
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            detail='Username Ou Email Já exitem no Banco de Dados',
            status_code=HTTPStatus.CONFLICT,
        )


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=str,
)
def delete_user(user_id: int, session: SessionDB, current_user: CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Sem Permissão '
        )

    session.delete(current_user)
    session.commit()

    return f'Usuário {current_user.username} Deletado Com Sucesso'


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=schema.UserPublic,
)
def read_user(user_id: int, session: SessionDB):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            detail='Usuário Não Encontrado', status_code=HTTPStatus.NOT_FOUND
        )

    return db_user
