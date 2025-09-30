from fastapi.testclient import TestClient
from fastapi_zero.app import app
from fastapi_zero.models import TodoState
from fastapi_zero.schemas import UserPublic
from http import HTTPStatus
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tests.conftest import TodoFactory
from fastapi_zero.models import Todo, TodoState

def test_create_todo(client, user, tokenGerado, mock_db_time):
    
        response = client.post('/todos/', 
                           headers={'Authorization': f'Bearer {tokenGerado}'},
                           json={
                               'title': 'Test Todo',
                               'description': 'Descricao Test',
                               'state': 'todo'
                               }
                           )
    
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {
                                    'id': 1,
                                'title': 'Test Todo',
                                'description': 'Descricao Test',
                                'state': 'todo',

                                }
    
def test_read_todo(client, tokenGerado):
    response = client.get('/todos/',
                          headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert response.json() == {'todos': []}
    assert response.status_code == HTTPStatus.OK
    
@pytest.mark.asyncio
async def test_read_todos_should_return(session,client, user, tokenGerado):

    #Arrange
    expected_todos = 5
    #Add All (colocar varios objt na sessão ao mesmo tempo)
    session.add_all(
        TodoFactory.create_batch(5, user_id= user.id))

    await session.commit()
    
    response = client.get('/todos/', headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_read_todos_with_filter_page(session, client, user, tokenGerado):
    
    expected = 2
    
    session.add_all(
        TodoFactory.create_batch(5, user_id = user.id)
    )
    
    await session.commit()
    
    response = client.get('/todos/?offset=1&limit=2', 
                          headers={'Authorization': f'Bearer {tokenGerado}'})

    assert len(response.json()['todos']) == expected
    
@pytest.mark.asyncio
async def test_read_todos_filter_title(session, client, user, tokenGerado):
    
    session.add_all(TodoFactory.create_batch(5, user_id = user.id, title = 'Teste Titulo'))
    
    session.add_all(TodoFactory.create_batch(5, user_id = user.id))

    
    await session.commit()
    
    response = client.get("/todos/?title=Teste Titulo",
                          headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert len(response.json()['todos']) == 5
    
@pytest.mark.asyncio
async def test_read_todos_filter_description(session, client, user, tokenGerado):
    
    session.add_all(TodoFactory.create_batch(5, user_id = user.id, description = 'descricao'))
    
    session.add_all(TodoFactory.create_batch(5, user_id = user.id, description = 'teste'))
    
    await session.commit()
    
    response = client.get("/todos/?description=desc",
                          headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert len(response.json()['todos']) == 5
    
@pytest.mark.asyncio
async def test_read_todos_filter_state(session, client, user, tokenGerado):
    
    session.add_all(TodoFactory.create_batch(5, user_id = user.id, state = TodoState.draft))
    
    
    await session.commit()
    
    response = client.get("/todos/?state=draft",
                          headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert len(response.json()['todos']) == 5
    
@pytest.mark.asyncio
async def test_delete_todo(session, client, user, tokenGerado):
    

    todo = TodoFactory(user_id = user.id)
    
    session.add(todo)
    await session.commit()
    
    response = client.delete(f'/todos/{todo.id}',
                             headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert response.json() == {'message': 'Tarefa Excluida Com Sucesso'}
    assert response.status_code == HTTPStatus.OK
    
    
def test_delete_not_exist_todo(client, tokenGerado):
    

    response = client.delete('/todos/10',
                             headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert response.json() == {'detail': 'Tarefa Não Encontrada'}
    assert response.status_code == HTTPStatus.NOT_FOUND
    
@pytest.mark.asyncio
async def test_delete_todo_other_user(client, tokenGerado, user, other_user, session):
    
    todo_other_user = TodoFactory(user_id = other_user.id)
    
    session.add(todo_other_user)
    await session.commit()
    
    response = client.delete(f'/todos/{todo_other_user.id}',
                             headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Tarefa Não Encontrada'}
    
@pytest.mark.asyncio
async def test_patch_todo(client, tokenGerado, user, session):
    
    todo1 = TodoFactory(user_id = user.id)
    
    session.add(todo1)
    await session.commit()
    
    response = client.patch(f'/todos/{todo1.id}',
                            json={'title': 'teste'},
                            headers={'Authorization': f'Bearer {tokenGerado}'})

    
    assert response.json()['title'] == 'teste'
    assert response.status_code == HTTPStatus.OK


def test_patch_not_exist_todo(client, tokenGerado):

    response = client.patch('/todos/10',
                             json={},
                             headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert response.json() == {'detail': 'Tarefa Não Encontrada'}
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_list_todos_should_return_all_field(session,client, tokenGerado, user, mock_db_time):
    
    todo = TodoFactory.create(user_id = user.id)
    session.add(todo)
    await session.commit()
        
    await session.refresh(todo)
    response = client.get('/todos/',
                             headers={'Authorization': f'Bearer {tokenGerado}'})
    
    assert response.json()['todos'] == [{
        'description': todo.description,
        'id': todo.id,
        'state': todo.state,
        'title': todo.title,
    }]
   
# @pytest.mark.asyncio
# async def test_create_todo_error(client, user, tokenGerado, session):
    
#      todo = Todo(
#         title="Teste",
#         description="Teste123",
#         state='teste',
#         user_id=user.id
#      )
     
#      session.add(todo)
#      await session.commit()
     
     
#     #  with pytest.raises(LookupError):
#     #     await session.scalar(select(Todo))
    
@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_fields__exercicio(
    session, client, user, tokenGerado, mock_db_time
):
    todo = TodoFactory.create(user_id=user.id)
    session.add(todo)
    await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {tokenGerado}'},
    )

    assert response.json()['todos'] == [{
        'description': todo.description,
        'id': todo.id,
        'state': todo.state,
        'title': todo.title,
    }]
    

        
def test_list_todos_filter_min_length_exercicio_06(client, tokenGerado):
    tiny_string = 'a'
    response = client.get(
        f'/todos/?title={tiny_string}',
        headers={'Authorization': f'Bearer {tokenGerado}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_todos_filter_max_length_exercicio_06(client, tokenGerado):
    large_string = 'a' * 22
    response = client.get(
        f'/todos/?title={large_string}',
        headers={'Authorization': f'Bearer {tokenGerado}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY