from pydantic_settings import BaseSettings, SettingsConfigDict

#Vamos Tirar a configuração do banco e mandar pro .env

class Settings(BaseSettings):
    model_config = SettingsConfigDict( 
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str