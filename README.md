<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/wordmark-dark.svg">
    <img alt="prompt-autoimprove" src="docs/assets/wordmark.svg" height="72">
  </picture>
</p>

[![DOI](https://zenodo.org/badge/1240262549.svg)](https://doi.org/10.5281/zenodo.20263523)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

`prompt-autoimprove` is a Python service for improving prompts before they are
sent to large language or multimodal models. It normalizes a raw request,
classifies the task, generates strategy-driven candidates, scores them, routes
the best revision to a target profile, optionally runs a model probation probe,
and records an explanation for the decision.

## Features

- Normalization pipeline: language detection, task classification, missing
  parameter detection, PII redaction, and safety flags.
- Six prompt-improvement strategies: role-based, structured-output,
  chain-decomposition, few-shot, self-verification, and multimodal adaptation.
- Pluggable model adapters behind one `ModelAdapter` protocol.
- Profile registry for Qwen, Llama, Gemma, multimodal `gemma-4-e2b`, and
  Anthropic Claude profiles.
- Integrated quality score:
  `S = 0.30·q_c + 0.25·q_p + 0.20·q_s + 0.15·q_t + 0.10·q_l`.
- FastAPI HTTP API, SSE stream at `/v1/improve/stream`, and gRPC
  server-streaming `AutoImproveService`.
- Persistence with SQLAlchemy 2 and Alembic; pipeline events through Kafka
  compatible with Redpanda in development.
- Reflex web frontend with Radix Themes; see [docs/frontend.md](docs/frontend.md).
- CLI entry point: `pai improve --prompt ... --profile qwen3-7b`.

Russian documentation is available in [README.ru.md](README.ru.md) and in the
MkDocs site under `/ru/`.

## Quickstart

```bash
uv sync --all-groups
uv run prek install --hook-type pre-commit --hook-type commit-msg
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Common commands

```bash
uv run ruff check .                                                      # lint
uv run ruff format .                                                     # format
uv run ty check src                                                      # typecheck
uv run pytest -q                                                         # tests
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000  # HTTP API + embedded gRPC
uv run pai serve-grpc                                                    # gRPC server only
./scripts/gen_proto.sh                                                   # regenerate gRPC stubs
uv run alembic upgrade head                                              # apply migrations (local)
docker compose up -d                                                     # postgres + redpanda + minio
docker compose --profile app up --build                                  # app + frontend stack
```

The HTTP app launches the gRPC `AutoImproveService` (port 50051) in the same
process by default; set `PAI_API__GRPC_ENABLED=false` to disable it, or run a
standalone gRPC process with `uv run pai serve-grpc`. Under docker compose the
`migrate` service runs `alembic upgrade head` before the app starts, and the
frontend depends on a healthy backend, so starting the web client brings up the
HTTP and gRPC interfaces with it.

## Web client

```bash
uv sync --group frontend
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Open <http://localhost:3000>. The frontend guide covers the layout in
[docs/frontend.md](docs/frontend.md), and [docs/local-models.md](docs/local-models.md)
shows how to run the pipeline against Ollama, LM Studio, GGUF, or Hugging Face
models.

## Documentation

```bash
uv run mkdocs serve
uv run mkdocs build --strict
```

The MkDocs site builds English at `/` and Russian at `/ru/`.

## Configuration

Environment variables use the `PAI_*` prefix where the service owns the setting.
Adapter-specific variables such as `OPENAI_BASE_URL` and `ANTHROPIC_API_KEY`
are documented in the model guides. Alembic reads its configuration from
`[tool.alembic]` in [pyproject.toml](pyproject.toml).

Migrations own the schema: set `PAI_DB__AUTO_CREATE=1` only to let the app
create tables directly for a quick local run without Alembic. `GET /healthz`
reports orchestrator and persistence readiness for container probes.

## License

GNU AGPL-3.0-or-later; see [LICENSE](LICENSE). AGPL-3.0 is a strong copyleft
license with a network-use clause: if you run a modified version of this service
and let users interact with it over a network, you must offer them the
corresponding source code.
