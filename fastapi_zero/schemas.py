# Definir uns contratos com o pydantic
# Deixar A Api Burocratica e aprova de loucura
# Tipo o Validation no Spring boot
from pydantic import BaseModel, EmailStr, ConfigDict
 


# Aplicando esse mano no end point ele vai definir que o corpo da requisição retorna um json, e  não uma string em formato json
# Impede de enviar informaões erradas
# Uma Maneira de  validar a entrada e saida de dados
class Message(BaseModel):
    message: str


# Criação da classe em si
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


# Porem Quero Retornar apenas o necessario para o cliente
# Assim Criamos o UserPublic


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)



class UserList(BaseModel):
    users: list[UserPublic]

class Token(BaseModel):
    access_token: str; # O Token jwt que vamos gerar
    token_type: str; # O Modelo que o cliente deve usar para a autorização
    
    
