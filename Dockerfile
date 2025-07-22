FROM python:3.13

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libpq-dev \
        && \
    # Cleanup
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==2.1.1

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY chat_bot /app/chat_bot

RUN apt-get purge -y --auto-remove build-essential libffi-dev libpq-dev




EXPOSE 8080

ENTRYPOINT ["python", "-m", "chat_bot"]
