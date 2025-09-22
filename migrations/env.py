from logging.config import fileConfig
import asyncio


from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from alembic import context
from fastapi_zero.settings import Settings
from fastapi_zero.models import table_registry
#   A APLICAÇÃO E O BANCO VÃO DESAGUAR TUDO AQUI NAS MIGRATIONS
#   PARA NÓS TERMOS AS VERSÕES DO BANCO 

#AQUI AONDE CONFIGURAREMOS A MIGRAÇÃO
#Temos que avisa ele aonfde esta no nosso banco de dados e como configura ele
#E Falar aonde estao os table_registry

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option('sqlalchemy.url', Settings().DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = table_registry.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
        
#DEIXANDO AS MIGRAÇÕES ASSINCRONAS
#Porem a migrações são sincronas mas o banco não está,
# por isso temos que dividir essas funções do migrations apenas para rodar a engine da migrção assincrona enquanto o resto não
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()
        
#A engine é assincrona
async def run_async_migrations_online():

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()



def run_migrations_online() -> None:
    asyncio.run(run_async_migrations_online())

#fim deixando as migrações assincronas

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
