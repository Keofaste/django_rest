FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VERSION=1.1.14

RUN useradd -m app
USER app

WORKDIR /home/app/django_rest

RUN mkdir -p /home/app/data/ \
    /home/app/data/logs/app \
    /home/app/data/csv \
    /home/app/data/static

RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
ENV PATH=/home/app/.local/bin:$PATH
RUN poetry config virtualenvs.in-project false

COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-interaction

COPY ./src ./src
COPY ./entrypoint.sh ./
