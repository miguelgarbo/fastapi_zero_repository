from fastapi_zero.schemas import UserPublic
from http import HTTPStatus
from fastapi_zero.models import User


def test_create_user(client, mock_db_time):

    # with mock_db_time(model=User) as time:
    response = client.post(
            '/users',
            json={
                'username': 'Bob',
                'email': 'bob@example.com',
                'password': 'secret',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'Bob',
        'email': 'bob@example.com',
       
    }


def test_read_users_with_users(client, user, tokenGerado):
    response = client.get(
        '/users', headers={'Authorization': f'Bearer {tokenGerado}'}
    )

    # Ou Seja Valida se oque vai voltar vai ser o UserPublic, aquele schema sem a password, e sem createdDate

    user_schema = UserPublic.model_validate(user).model_dump()
    

    assert response.json() == {
        'users': [
            user_schema
            # {
            #     'email': 'teste@email.com',
            #     'id':1,
            #     'username': 'teste'
            # }
        ]
    }
    assert response.status_code == HTTPStatus.OK


def test_update_user(client, user, tokenGerado):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {tokenGerado}'},
        json={
            'username': 'Patrick',
            'email': 'patrick@example.com',
            'password': 'secret2',
        },
    )

    assert response.json() == {
        'username': 'Patrick',
        'email': 'patrick@example.com',
        'id': user.id,
    }

    assert response.status_code == HTTPStatus.OK


def test_delete_user(client, user, tokenGerado):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {tokenGerado}'}
    )

    assert response.json() == f'Usuário {user.username} Deletado Com Sucesso'

    assert response.status_code == HTTPStatus.OK


def test_delete_user_error_validation(client, user, tokenGerado):
    response = client.delete(
        'users/-10', headers={'Authorization': f'Bearer {tokenGerado}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem Permissão '}


def test_update_user_error_validation(client, tokenGerado):
    response = client.put(
        'users/-10',
        headers={'Authorization': f'Bearer {tokenGerado}'},
        json={
            'username': 'Patrick',
            'email': 'patrick@example.com',
            'password': 'secret2',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem Permissão'}


def test_update_integrity_error(client, user,other_user, tokenGerado):


    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {tokenGerado}'},
        json={
            'username': other_user.username,
            'email': other_user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username Ou Email Já exitem no Banco de Dados'
    }


def test_username_exist(client, user):
    response = client.post(
        '/users/',
        json={
            'username': f'{user.username}',
            'email': 'miguel@gmail.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Esse UserName Já Existe no Banco'}


def test_email_exist(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'miguel',
            'email': f'{user.email}',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Esse Email Já Existe No Banco'}


def test_find_by_id(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/1')

    assert response.json() == user_schema
    assert response.status_code == HTTPStatus.OK


def test_not_find_by_id(client, user):
    response = client.get('/users/2')

    assert response.json() == {'detail': 'Usuário Não Encontrado'}
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_user_with_wrong_user(client,other_user, tokenGerado):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {tokenGerado}'},
        json={
            'username': 'Miguel',
            'email': 'miguel@example.com',
            'password': 'newPassword'
            
        })
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail':'Sem Permissão'}
    
    
