import asyncio
import sys
from fastapi import FastAPI
from http import HTTPStatus
import fastapi.responses as response
import fastapi_zero.schemas as schema
from fastapi_zero.routers import auth, users, todo

if sys.platform == 'win32': 
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title='API..')

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todo.router)


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=schema.Message,
    response_class=response.JSONResponse,
)
async def read_root():
    return schema.Message(message='Olá Mundo!')

