FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    swig \
    libssl-dev \
    dpkg-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.7.14 /uv /uvx /bin/

ADD . /code
WORKDIR /code

RUN uv sync --locked --no-dev

RUN uv run --no-dev manage.py collectstatic --noinput
