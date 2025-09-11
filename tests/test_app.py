from fastapi.testclient import TestClient
from fastapi_zero.app import app
from http import HTTPStatus
from tests.conftest import client
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


def test_root_deve_retornar_ola_mundo():
    # Arrange
    # client = TestClient(app)

    # Act
    # Vai la e faz uma requisição desse caminho
    # Encapsula a resposta do metodo numa variavel
    response = client.get('/')

    # Assert confirma se é verdadeiro, só verifica se é verdadeiro e manda um bug se não estiver
    assert response.json() == {'message': 'Olá Mundo!'}
    assert response.status_code == HTTPStatus.OK


def test_getHtml_deve_retornar_html():
    # client = TestClient(app)

    response = client.get('/htmlEndPoint')

    assert response.status_code == HTTPStatus.OK
    assert '<h1> Olá Mundo</h1>' in response.text


def test_create_user():
    # client = TestClient(app)

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


def test_read_users():
    response = client.get('/users')

    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'Bob',
                'email': 'bob@example.com',
            }
        ]
    }
    assert response.status_code == HTTPStatus.OK


def test_update_user():
    response = client.put(
        '/users/1',
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
    
    
def test_delete_user():
    response = client.delete(
        '/users/1'
    )

    assert response.json() == {
        'username': 'Patrick',
        'email': 'patrick@example.com',
        'id': 1,
    }

    assert response.status_code == HTTPStatus.OK    
    
    
def test_delete_user_error_validation():
    response = client.delete(
        'users/-10'
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário Não Encontrado'}
    


def test_update_user_error_validation():
    response = client.put(
        'users/-10',
        json={
            'username': 'Patrick',
            'email': 'patrick@example.com',
            'password': 'secret2',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário Não Encontrado'}
