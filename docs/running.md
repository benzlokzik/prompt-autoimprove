# Running the service

This page covers running `prompt-autoimprove` end to end — with Docker Compose
for the full stack, or locally for development.

## With Docker Compose

```bash
docker compose up -d --build app
```

Compose starts the dependencies in order and waits for each to be healthy:

1. **postgres** — application database.
2. **redpanda** — Kafka-compatible event broker.
3. **migrate** — one-shot job that runs `alembic upgrade head`, then exits. The
   app does **not** start until migrations succeed.
4. **app** — FastAPI HTTP API on `:8000` and the gRPC `AutoImproveService` on
   `:50051` in the same process.

Bring up the web client (built with `reflex --env prod`) separately:

```bash
docker compose up -d --build frontend   # http://localhost:3000
```

`minio` is included for artifact storage but nothing depends on it. Check
readiness:

```bash
curl http://localhost:8000/healthz
# {"status":"ok","orchestrator":true,"persistence":true}
```

| Service | Port(s) | Notes |
| --- | --- | --- |
| app (HTTP) | 8000 | `/docs`, `/healthz`, `/v1/*` |
| app (gRPC) | 50051 | `AutoImproveService`; disable with `PAI_API__GRPC_ENABLED=false` |
| frontend | 3000 | Reflex UI (state backend on 8001) |
| postgres | 5432 | |
| redpanda | 19092 | external Kafka listener |
| minio | 9000 / 9001 | API / console |

Tear down (drop volumes to reset the database):

```bash
docker compose down -v
```

## Locally (no Docker)

```bash
uv sync
uv run alembic upgrade head            # or set PAI_DB__AUTO_CREATE=1 for a throwaway DB
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000
```

Other entry points share the same pipeline runtime:

```bash
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b   # CLI
uv run pai serve-grpc                                                # gRPC only
uv run pai profiles                                                  # list profiles
```

A database is optional for the HTTP/CLI happy path — without one the service
runs in improvement-only mode and history is not persisted (`/healthz` reports
`persistence: false`).

## Configuration

All service settings use the `PAI_*` prefix with `__` as the nested delimiter.

| Variable | Default | Purpose |
| --- | --- | --- |
| `PAI_API__API_KEY` | `dev-key` in dev | Required outside dev unless `PAI_API__ALLOW_DEV_KEY=1`. |
| `PAI_API__GRPC_ENABLED` | `true` | Start the in-process gRPC server. |
| `PAI_API__CORS_ORIGINS` | localhost:3000 | Comma-separated allowed origins. |
| `PAI_DB__DSN` | local Postgres | SQLAlchemy async DSN. |
| `PAI_DB__AUTO_CREATE` | `false` | Create tables on boot instead of using migrations (dev only). |
| `PAI_KAFKA__ENABLED` | `false` | Publish pipeline events to Kafka/Redpanda. |
| `PAI_CLASSIFIER__BACKEND` | `heuristic` | `heuristic`, `embeddings`, `judge`, or `composite`. |
| `PAI_SCORER__SEMANTIC` | `false` | Blend embedding intent-similarity into scoring (needs the `ml` group). |

## Optional dependency groups

```bash
uv sync --group ml             # tiktoken tokenizer, embeddings, semantic scorer
uv sync --group local-models   # llama.cpp / GGUF local inference
uv sync --group frontend       # Reflex web client
```

The Docker image accepts `--build-arg INCLUDE_ML=1` and
`--build-arg INCLUDE_LOCAL_MODELS=1` to bake these in.
