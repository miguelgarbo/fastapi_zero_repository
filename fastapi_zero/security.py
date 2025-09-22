from pwdlib import PasswordHash
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jwt import encode, decode, DecodeError
from fastapi_zero.database import get_session
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from http import HTTPStatus
from sqlalchemy import select
from fastapi_zero.models import User
from fastapi_zero.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession




# Criar um contexto de criptografia
# Nós pegamos as recomendações da biblioteca

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
settings = Settings()

# Função que vai ler a senha limpa e vai gerar um hash dessa senha
def get_password_hash(password: str):
    return pwd_context.hash(password)


# Passa a Senha Limpa, ele vai encriptar essa senha e ve se o hash é o mesmo que ta no banco
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    # Payload
    # Criar todas as claims(alegações) aqui
    to_encode = data.copy()

    # Aqui A gente define o tempo do token
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})

    encode_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encode_jwt



async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Não foi Possivel Autorizar',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        # Nesse decode é onde é retornado as claims que ficam dentro do payload
        payload = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        # Nós queremos achar o subject(assunto do token) email no nosso caso
        # Se nao vier o email dá um erro

        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    user = await session.scalar(select(User).where(User.email == subject_email))

    if not user:
        raise credentials_exception

    return user
