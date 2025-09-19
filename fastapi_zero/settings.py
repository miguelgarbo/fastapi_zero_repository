from pydantic_settings import BaseSettings, SettingsConfigDict


# Aqui está configurando o caminho do nosso banco de dados
# Onde essa função traz o aquivo env onde nossa url do banco está


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str
    SECRET_KEY:str 
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
