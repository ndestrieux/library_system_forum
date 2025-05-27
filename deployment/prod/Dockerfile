FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=True \
    PYTHONUNBUFFERED=True
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

COPY ./src ./pyproject.toml ./poetry.lock ./README.md /app/

WORKDIR /app

RUN apk update \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip --no-cache \
    && pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-root \
    && rm -rf $POETRY_CACHE_DIR \
    && pip uninstall poetry -y

FROM python:3.12-alpine AS runner

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app /app
COPY ./deployment/prod/scripts/ /scripts

ENV PATH="/usr/local/bin:/scripts:$PATH"
RUN sed -i 's/\r$//' /scripts/run.sh \
    && chmod -R +x /scripts

ENV PATH="/scripts::$PATH"

CMD ["run.sh"]
