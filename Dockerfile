# syntax=docker/dockerfile:1

FROM python:3.14-slim AS builder

# hadolint ignore=DL3008 # Allow installing unversioned build-time Git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=0

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --all-groups --no-install-project

FROM python:3.14-slim

RUN useradd -m appuser && \
    mkdir -p /app /data && \
    chown appuser:appuser /app /data

WORKDIR /app
USER appuser

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
COPY --chown=appuser:appuser . .

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py"]
