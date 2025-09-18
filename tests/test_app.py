from fastapi.testclient import TestClient
from fastapi_zero.app import app
from fastapi_zero.schemas import UserPublic 
from http import HTTPStatus
# Transformou o app do app.py em cliente pro nosso test
# Para podermos conversar com ele(app.py)

# Explanation: Como funciona um test

# Passa por 3 Etapas (AAA)

# A = Arrange = Arranjo
# Pra chamar a função pro teste a gente precisa configurar coisas antes, essa etapa é o arrange
# A = Act = agir
# Depois disso precisamos agir, chama o blocoaquilo de codigo que queremos testar
# A = Assert = afirmar
# Garantir que A é A, garanta que a resposta deu certo de acordo com meus parametros


def test_root_deve_retornar_ola_mundo(client):
    # Arrange
    # client = TestClient(app)

    # Act
    # Vai la e faz uma requisição desse caminho
    # Encapsula a resposta do metodo numa variavel
    response = client.get('/')

    # Assert confirma se é verdadeiro, só verifica se é verdadeiro e manda um bug se não estiver
    assert response.json() == {'message': 'Olá Mundo!'}
    assert response.status_code == HTTPStatus.OK


def test_getHtml_deve_retornar_html(client):
    # client = TestClient(a.200pp)

    response = client.get('/htmlEndPoint')

    assert response.status_code == HTTPStatus.OK
    assert '<h1> Olá Mundo</h1>' in response.text


def test_create_user(client):
    # client = TestClient(app)

    response = client.post(
        '/users',
        json={
            'username': 'Bob',
            'email': 'bob@example.com',
            'password': 'secret',
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'Bob',
        'email': 'bob@example.com',
    }

def test_read_users_with_users(client, user, tokenGerado):
    response = client.get('/users', headers={'Authorization': f'Bearer {tokenGerado}'})
    
    #Ou Seja Valida se oque vai voltar vai ser o UserPublic, aquele schema sem a password, e sem createdDate
    
    user_schema = UserPublic.model_validate(user).model_dump()
    
    assert response.json() == {
        'users': [user_schema
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
        '/users/1',
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
        'id': 1,
    }

    assert response.status_code == HTTPStatus.OK
    
    
def test_delete_user(client, user, tokenGerado):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {tokenGerado}'}
    )

    assert response.json() == f"Usuário {user.username} Deletado Com Sucesso"

    assert response.status_code == HTTPStatus.OK    
    
    
def test_delete_user_error_validation(client, user, tokenGerado):
    response = client.delete(
        'users/-10',
        headers= {'Authorization': f'Bearer {tokenGerado}'}
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


def test_update_integrity_error(client, user, tokenGerado):
    
    client.post('/users/',
                
        json= {
            'username': 'Miguel',
            'email': 'miguel@gmail.com',
            'password': 'secret'
        })
    
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {tokenGerado}'},
        json={
            'username': 'Miguel1234',
            'email': 'miguel@gmail.com',
            'password': 'secret'
            }            
    )
    
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username Ou Email Já exitem no Banco de Dados'}

def test_username_exist(client, user):
    
    response = client.post('/users/', json=
        {
            'username': 'teste',
            'email': 'miguel@gmail.com',
            'password': 'secret'
        }        
        
    )

    assert response.status_code == HTTPStatus.CONFLICT 
    assert response.json() == {'detail':"Esse UserName Já Existe no Banco"}
    
def test_email_exist(client, user):
    
    response = client.post('/users/', json=
        {
            'username': 'miguel',
            'email': 'teste@email.com',
            'password': 'secret'
        }        
        
    )

    assert response.status_code == HTTPStatus.CONFLICT 
    assert response.json() == {'detail':"Esse Email Já Existe No Banco"}
    
def test_find_by_id(client, user):
    

    user_schema = UserPublic.model_validate(user).model_dump()


    response = client.get('/users/1')
    
    assert response.json() == user_schema
    assert response.status_code  == HTTPStatus.OK
    
def test_not_find_by_id(client, user):
    
    response = client.get('/users/2')
    
    assert response.json() == {'detail': 'Usuário Não Encontrado'}
    assert response.status_code  == HTTPStatus.NOT_FOUND
    
    
def test_get_token(client, user):
    
    response = client.post("/token",
        data={'username': user.email, 'password': user.clean_password}
        )
    
    token = response.json()
    
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'bearer'