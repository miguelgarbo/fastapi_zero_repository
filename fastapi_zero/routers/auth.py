from fastapi import HTTPException, Depends, APIRouter
from http import HTTPStatus
import fastapi_zero.schemas as schema
from fastapi_zero.models import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi_zero.database import get_session
from fastapi_zero.security import verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix='/auth', tags=['auth'])

FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDB = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post('/token', response_model=schema.Token)
async def login_for_access_token(form_data: FormData,session: SessionDB):
    
    user = await session.scalar(select(User).where(User.email == form_data.username))

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
    return {'access_token': access_token, 'token_type': 'Bearer'}

@router.post('/refresh_user_token', response_model= schema.Token)
async def refresh_token(user_current: CurrentUser):
    new_access_token = create_access_token(data={'sub': user_current.email})
    
    return {'access_token': new_access_token, 'token_type': 'Bearer'}
