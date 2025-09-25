from fastapi import HTTPException, Depends, APIRouter, Query
from http import HTTPStatus
import fastapi_zero.schemas as schema
from fastapi_zero.models import User, Todo
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi_zero.database import get_session
from fastapi_zero.security import get_current_user
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/todos', tags=['todos'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session =Annotated[AsyncSession, Depends(get_session)]
FilterTodoPage = Annotated[schema.FilterTodo, Query()]

@router.post("/", response_model=schema.TodoPublic, status_code=HTTPStatus.CREATED)
async def create_todo(todo:schema.TodoSchema
                      , sessionAsync: Session
                      , currentUser: CurrentUser):
    
    todo_new = Todo(user_id=currentUser.id, title=todo.title, 
                description=todo.description, state = todo.state)
    
    sessionAsync.add(todo_new)
    await sessionAsync.commit()
    await sessionAsync.refresh(todo_new)
    
    return todo_new

@router.get('/', response_model= schema.TodoList)
async def read_todos(sessionAsync: Session, currentUser: CurrentUser, filterTodo: FilterTodoPage):
    
    query = select(Todo).where(Todo.user_id == currentUser.id)
    
    #Se tiver o campo title com algo dentro ele vai executar a query
    if filterTodo.title:
        #Ele vai adicionar outro where na query base que esta acima, ou seja vai pegar os todos de um usuario e filtrar o tittle
      query =  query.filter(Todo.title.contains(filterTodo.title))
        
    if filterTodo.description:
        query = query.filter(Todo.description.contains(filterTodo.description))
        
    if filterTodo.state:
        query = query.filter(Todo.state == filterTodo.state)
        
        
    todos = await sessionAsync.scalars(query.limit(filterTodo.limit).offset(filterTodo.offset))
    
    
    return {'todos': todos}

@router.delete('/{todo_id}', response_model=schema.Message)
async def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )
    
    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, 
                            detail="Tarefa Não Encontrada")
    if todo.user_id != user.id:
         raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, 
                            detail="Não Autorizado A Deletar Tarefa de Outro Usuário")
        
    
    await session.delete(todo)
    await session.commit()
    
    return {'message': 'Tarefa Excluida Com Sucesso'}

@router.patch('/{todo_id}', response_model=schema.TodoPublic)
async def patch_todo(todo_id: int, todoNewInfo: schema.TodoUpdate, 
                     current_user: CurrentUser, session: Session):
    
    todoDB = await session.scalar(select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id))
    
    if not todoDB:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Tarefa Não Encontrada')
        
        #Atualiza os atributos um por um, de acordo com as chaves e valor recebidas no body
        #E Atualiza A todo do banco, a todo id da url
    for chave, valor in todoNewInfo.model_dump(exclude_unset=True).items():
        setattr(todoDB, chave, valor)
        
        
    session.add(todoDB)     
    await session.commit()
    await session.refresh(todoDB)    
    
    return todoDB
    
    