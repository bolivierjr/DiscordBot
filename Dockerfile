FROM python:3.7-slim

WORKDIR /bot

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=false \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.1.11

RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false --local
RUN poetry config virtualenvs.in-project false --local
RUN poetry install --no-interaction --no-ansi --no-dev

COPY . .

CMD ["python3", "-m", "discord_bot"]
