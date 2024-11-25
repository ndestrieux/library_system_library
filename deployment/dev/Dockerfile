FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY ./src ./pyproject.toml ./poetry.lock ./README.md /app/
COPY ./deployment/dev/scripts/ /scripts

RUN poetry config virtualenvs.create false \
    && poetry install && \
    sed -i 's/\r$//' /scripts/run.sh && \
    chmod -R +x /scripts

ENV PATH="/scripts::$PATH"

CMD ["run.sh"]
