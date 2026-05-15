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

## Verification

`tests/integration/test_ollama_probation.py` skips when nothing is listening on
`localhost:11434`, so CI stays independent of Ollama while local runs can
exercise the adapter, orchestrator, and probation path.

```bash
OLLAMA_HOST=localhost:11434 uv run pytest tests/integration/test_ollama_probation.py -v
```
