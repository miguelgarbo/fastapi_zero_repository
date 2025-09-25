# Definir uns contratos com o pydantic
# Deixar A Api Burocratica e aprova de loucura
# Tipo o Validation no Spring boot
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from fastapi_zero.models import TodoState


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
    
class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


# Porem Quero Retornar apenas o necessario para o cliente
# Assim Criamos o UserPublic


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
    
class TodoPublic(TodoSchema):
    id:int


class UserList(BaseModel):
    users: list[UserPublic]
    
class TodoList(BaseModel):
    todos: list[TodoPublic]


class Token(BaseModel):
    access_token: str  # O Token jwt que vamos gerar
    token_type: str  # O Modelo que o cliente deve usar para a autorização

class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0 );
    limit:int = Field(ge=0, default=10)
    
class FilterTodo(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=20)
    description: str | None = None
    state: TodoState | None = None
    
class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None