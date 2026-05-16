FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ARG INCLUDE_ML=0
ARG INCLUDE_LOCAL_MODELS=0

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    EXTRA_GROUPS="" && \
    if [ "$INCLUDE_ML" = "1" ]; then EXTRA_GROUPS="$EXTRA_GROUPS --group ml"; fi && \
    if [ "$INCLUDE_LOCAL_MODELS" = "1" ]; then EXTRA_GROUPS="$EXTRA_GROUPS --group local-models"; fi && \
    uv sync --frozen --no-install-project --no-dev $EXTRA_GROUPS

COPY src ./src
COPY proto ./proto
COPY scripts ./scripts

RUN --mount=type=cache,target=/root/.cache/uv \
    EXTRA_GROUPS="" && \
    if [ "$INCLUDE_ML" = "1" ]; then EXTRA_GROUPS="$EXTRA_GROUPS --group ml"; fi && \
    if [ "$INCLUDE_LOCAL_MODELS" = "1" ]; then EXTRA_GROUPS="$EXTRA_GROUPS --group local-models"; fi && \
    uv sync --frozen --no-dev $EXTRA_GROUPS


FROM python:3.13-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin pai

COPY --from=builder --chown=pai:pai /app /app

USER pai

EXPOSE 8000 50051

CMD ["uvicorn", "prompt_autoimprove.api.http.app:app", "--host", "0.0.0.0", "--port", "8000"]
