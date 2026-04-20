# prompt-autoimprove

Microservices system that automatically improves prompts for large language and
multimodal models. It normalizes a raw user prompt, classifies the underlying
task, generates strategy-driven candidate prompts, routes them to a target
model (local GGUF, HuggingFace safetensors, or OpenAI-compatible API),
evaluates the result with a hybrid score, and explains its decision.

## Features

- Normalization pipeline: language detection, task classification, missing
  parameter detection, safety guards.
- Six prompt-improvement strategies: role-based, structured-output,
  chain-decomposition, few-shot, self-verification, multimodal adaptation.
- Pluggable model adapters with a single `ModelAdapter` protocol.
- Profile registry for Qwen, Llama, Gemma families (text + vision).
- Integrated quality score `S = 0.30·q_c + 0.25·q_p + 0.20·q_s + 0.15·q_t + 0.10·q_l`.
- HTTP API (FastAPI) and gRPC server-streaming `AutoImproveService`.
- Persistence via SQLAlchemy 2 + Alembic; events via Kafka.
- CLI: `pai improve --prompt ... --profile qwen3-7b`.

## Quickstart

```bash
uv sync --all-groups
uv run prek install --hook-type pre-commit --hook-type commit-msg
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Development

```bash
uv run ruff check .
uv run ruff format .
uv run ty check src
uv run pytest -q
```

## License

MIT — see [LICENSE](LICENSE).
