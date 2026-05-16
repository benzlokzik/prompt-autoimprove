# Running against a local model

`OpenAICompatAdapter` speaks any OpenAI-compatible chat completions API. The
project has been validated against three local backends on an M-series MacBook.

## Ollama

```bash
brew install ollama
ollama serve &
ollama pull qwen2.5:1.5b-instruct      # about 1.0 GB, fast on CPU/MPS
```

Wire the adapter through environment variables:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_TARGET_PROFILE=ollama-qwen-1_5b
export OPENAI_MODEL_NAME=qwen2.5:1.5b-instruct
```

The shipped `ollama-qwen-1_5b` profile in
`src/prompt_autoimprove/registry/profiles/` is tuned for this model: 32k
context, 1k output tokens, and about 800 ms p50 latency.

Smoke test:

```bash
uv run pai improve --prompt "Summarize this article" --profile ollama-qwen-1_5b
```

You should see a **Probation output** section with a real model reply.

## LM Studio

```bash
lms get qwen2.5-1.5b-instruct
lms server start          # exposes an OpenAI-compatible API on :1234
```

Use the same environment wiring with
`OPENAI_BASE_URL=http://localhost:1234/v1`.

## Hugging Face direct

Pull a small instruct model with the authenticated CLI:

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b
# OR a GGUF:
hf download bartowski/Qwen2.5-1.5B-Instruct-GGUF \
  qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/
```

Then point either `SafetensorsHFAdapter` (`uv add transformers torch`) or
`GGUFAdapter` (`uv add llama-cpp-python`) at the file. Both options are heavier
on macOS than Ollama and are mainly useful when you need direct control over
model loading.

## Complexity classifier backends

The orchestrator decides whether to escalate a prompt to the LLM rewriter using
a `ComplexityClassifier`. Pick one via `PAI_CLASSIFIER__BACKEND`:

| Backend | What it does | Cost / latency | When to use |
|---|---|---|---|
| `heuristic` (default) | Pure-Python rules on length, task, params, ambiguity. | ~µs, zero deps. | Production default. |
| `embeddings` | Cosine similarity to curated simple/hard centroids via `sentence-transformers/all-MiniLM-L6-v2`. | ~10 ms after warm-up; needs `uv sync --group ml`. | When you want ML quality with no per-call cost. |
| `judge` | Sends a one-word "simple/hard" judgement to the configured improver `ModelAdapter`. Cached on prompt hash. | One small LLM call per uncached prompt. | Highest quality, predictable budget. |
| `composite` | Heuristic first; consults the embedding backend only when heuristic score lands in `[composite_lo, composite_hi]`. | Mostly free, ML on borderline. | Recommended when you've installed the `ml` group. |

Other knobs: `PAI_CLASSIFIER__EMBEDDING_MODEL`, `PAI_CLASSIFIER__DEVICE`,
`PAI_CLASSIFIER__COMPOSITE_LO`, `PAI_CLASSIFIER__COMPOSITE_HI`.

## Verification

`tests/integration/test_ollama_probation.py` skips when nothing is listening on
`localhost:11434`, so CI stays independent of Ollama while local runs can
exercise the adapter, orchestrator, and probation path.

```bash
OLLAMA_HOST=localhost:11434 uv run pytest tests/integration/test_ollama_probation.py -v
```

The `scripts/local_e2e.py` helper runs the full classifier + rewriter pipeline
against any local Ollama tag and prints both the rewritten candidate and the
final chosen prompt:

```bash
uv run python scripts/local_e2e.py ollama-qwen3-1_7b qwen3:1.7b
```
