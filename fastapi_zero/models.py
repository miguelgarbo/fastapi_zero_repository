from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

#ISso vai registrar as coisas que serao mapeadas entre a aplicacao, as tabelas python e as tabelas do banco
table_registry = registry()


@table_registry.mapped_as_dataclass
class User():
    __tablename__ =  'users'
    
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    
    #Pega exatamente a hora minuto e segundo quando a requisição chegar ao banco de dados
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now())
    
