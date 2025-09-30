FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR app/
COPY . . 

RUN pip install poetry 
RUN poetry install --no-interaction --no-ansi --without dev
RUN poetry config installer.max-workers 10

EXPOSE 8000
CMD poetry run uvicorn --host 0.0.0.0 fastapi_zero.app:app

