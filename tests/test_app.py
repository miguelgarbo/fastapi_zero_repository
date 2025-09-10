from fastapi.testclient import TestClient
from fastapi_zero.app import app
from http import HTTPStatus


#Transformou o app do app.py em cliente pro nosso test
#Para podermos conversar com ele(app.py)

#Explanation: Como funciona um test

#Passa por 3 Etapas (AAA)

# A = Arrange = Arranjo 
# Pra chamar a função pro teste a gente precisa configurar coisas antes, essa etapa é o arrange 
# A = Act = agir
#Depois disso precisamos agir, chama o blocoaquilo de codigo que queremos testar
# A = Assert = afirmar
#Garantir que A é A, garanta que a resposta deu certo de acordo com meus parametros



def test_root_deve_retornar_ola_mundo():
    client = TestClient(app)


    #Vai la e faz uma requisição desse caminho 
    #Encapsula a resposta do metodo numa variavel
    response = client.get('/')
    
    #Assert confirma se é verdadeiro, só verifica se é verdadeiro e manda um bug se não estiver
    assert response.json() == {'message': 'Olá Mundo!'}
    assert response.status_code == HTTPStatus.OK