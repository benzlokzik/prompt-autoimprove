# prompt-autoimprove

Microservices system that automatically improves prompts for large language and
multimodal models.

## What it does

1. **Normalize** the raw user prompt — clean control chars, detect language and
   task type, surface missing parameters, redact PII, raise safety flags.
2. **Generate candidates** with up to six strategies: role-based, structured
   output, chain decomposition, few-shot, self-verification, multimodal.
3. **Score** every candidate with the integrated formula
   `S = 0.30·q_c + 0.25·q_p + 0.20·q_s + 0.15·q_t + 0.10·q_l`.
4. **Route** the winner to a target model — local GGUF, HF safetensors,
   OpenAI-compatible API, or Anthropic Claude.
5. **Probate** (optionally) on the chosen model and persist the run.
6. **Explain** the decision in human terms.

## Quickstart

```bash
uv sync --all-groups
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Browse the docs

- [Architecture](architecture.md) — components and data flow.
- [Strategies](strategies.md) — what each improvement strategy does.
- [Scoring](scoring.md) — the integrated metric.
- [CLI](cli.md) — `pai` command reference.

## Develop the docs

```bash
uv run mkdocs serve   # live preview at http://127.0.0.1:8000
uv run mkdocs build   # static site in ./site
```
