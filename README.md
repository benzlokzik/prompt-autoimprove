# prompt-autoimprove

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
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000  # HTTP API
uv run python -m prompt_autoimprove.api.grpc.server                      # gRPC server
./scripts/gen_proto.sh                                                   # regenerate gRPC stubs
uv run alembic upgrade head                                              # apply migrations
docker compose up -d                                                     # postgres + redpanda + minio
docker compose --profile app up --build                                  # app + frontend stack
```

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

## License

MIT; see [LICENSE](LICENSE).
