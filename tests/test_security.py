from fastapi_zero.security import create_access_token, SECRET_KEY, ALGORITHM
from jwt import decode
from http import HTTPStatus

def test_jwt():
    
    data = {'test': 'test'}
    
    token = create_access_token(data) 
    
    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)
        
    assert decoded['test'] == data['test']
    assert 'exp' in decoded
    
def test_jwt_invalid(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer blabla'}
    )
    
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não foi Possivel Autorizar'}
    


def test_jwt_current_user_not_sub(client):
    data = {'no-email': 'test'}
    
    token = create_access_token(data)
    
    response = client.delete(
        '/users/1', 
        headers= {'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail':'Não foi Possivel Autorizar'}

def test_jwt_current_user(client):
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)
    
    response = client.put('/users/1',
                headers= {'Authorization': f'Bearer {token}'},
                json={'username': 'TESTEEEEEEE','email': 'TESTEEEEE', 'password': 'TESTEEE'}
                )
    
    assert response.json() == {'detail':'Não foi Possivel Autorizar'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_current_user_does_not_exists__exercicio(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail':'Não foi Possivel Autorizar'}
    
    
    
    