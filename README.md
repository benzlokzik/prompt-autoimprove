# prompt-autoimprove

Microservices system that automatically improves prompts for large language and
multimodal models. It normalizes a raw user prompt, classifies the underlying
task, generates strategy-driven candidate prompts, routes them to a target
model (local GGUF, HuggingFace safetensors, or OpenAI-compatible / Anthropic
API), evaluates the result with a hybrid score, and explains its decision.

## Features

- Normalization pipeline: language detection, task classification, missing
  parameter detection, safety guards.
- Six prompt-improvement strategies: role-based, structured-output,
  chain-decomposition, few-shot, self-verification, multimodal adaptation.
- Pluggable model adapters with a single `ModelAdapter` protocol.
- Profile registry for Qwen, Llama, Gemma (incl. multimodal `gemma-4-e2b`)
  and Anthropic Claude.
- Integrated quality score `S = 0.30·q_c + 0.25·q_p + 0.20·q_s + 0.15·q_t + 0.10·q_l`.
- HTTP API (FastAPI) and gRPC server-streaming `AutoImproveService`.
- SSE pipeline stream at `/v1/improve/stream` for live UI updates.
- Persistence via SQLAlchemy 2 + Alembic; events via Kafka (Redpanda in dev).
- Reflex web frontend with dark Radix theme — see [docs/frontend.md](docs/frontend.md).
- CLI: `pai improve --prompt ... --profile qwen3-7b`.

## Quickstart

```bash
uv sync --all-groups
uv run prek install --hook-type pre-commit --hook-type commit-msg
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Commands

```bash
uv run ruff check .                                                      # lint
uv run ruff format .                                                     # format
uv run ty check src                                                      # typecheck
uv run pytest -q                                                         # tests
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000  # http api
uv run python -m prompt_autoimprove.api.grpc.server                      # grpc server
./scripts/gen_proto.sh                                                   # regen grpc stubs
uv run alembic upgrade head                                              # apply migrations
docker compose up -d                                                     # postgres + redpanda + minio
docker compose --profile app up --build                                  # full stack incl. app + frontend
```

## Web client

```bash
uv sync --group frontend
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Open <http://localhost:3000>. See [docs/frontend.md](docs/frontend.md) for the
layout and [docs/local-models.md](docs/local-models.md) for running the
pipeline against a local Ollama / LM Studio / HF model.

## Configuration

Environment variables follow `PAI_*` (see `.env.example`). Alembic config
lives in `[tool.alembic]` in `pyproject.toml`.

## License

MIT — see [LICENSE](LICENSE).
