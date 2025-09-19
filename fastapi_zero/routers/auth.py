from fastapi import HTTPException, Depends, APIRouter
from http import HTTPStatus
import fastapi_zero.schemas as schema
from fastapi_zero.models import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi_zero.database import get_session
from fastapi_zero.security import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter(prefix='/auth', tags=['auth'])

FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDB = Annotated[Session, Depends(get_session)]

@router.post('/token', response_model=schema.Token)
def login_for_access_token(form_data: FormData,session: SessionDB,):
    
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}
