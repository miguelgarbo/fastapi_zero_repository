from http import HTTPStatus
from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'

def test_token_expires_30_min(client, user):
    #em teoria o token foi gerado por esse tempo
    #como nosso token dura 30min chamamos la em baixo 30 min a mais que esse pra ver se ta funcionando
    with freeze_time('2025-08-13 12:00:00'):
        responsePost = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password}
        )
        
        assert responsePost.status_code == HTTPStatus.OK
        token = responsePost.json()['access_token']
        
    with freeze_time('2025-08-13 12:31:00'):
        responsePut = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@example.com',
                'password': 'wrong'
            }
        )
        
        assert responsePut.status_code == HTTPStatus.UNAUTHORIZED
        assert responsePut.json() == {'detail':'Não foi Possivel Autorizar'}


def test_token_wrong_password(client, user):
    response = client.post('/auth/token', 
        data={'username': user.email, 'password': 'senhaErrada'}
        )
   
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
    
def test_token_user_not_exists(client, user):
    response = client.post('/auth/token', 
        data={'username': 'email@naoexisto.com', 'password': 'user123'}
        )
   
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
    
    
def test_refresh_token(client, user, tokenGerado):
    response = client.post(
        '/auth/refresh_user_token',
        headers={'Authorization': f'Bearer {tokenGerado}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2025-08-13 12:00:00'):
        response = client.post('/auth/token',
                data={'username': user.email, 'password': user.clean_password})
        
        token = response.json()['access_token']
        
    with freeze_time('2025-08-13 12:31:00'):
        response = client.post('/auth/refresh_user_token',
                               headers={'Authorization': f'Bearer {token}'})
        
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail':'Não foi Possivel Autorizar'}