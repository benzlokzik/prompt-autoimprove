# Running against a local model

The `OpenAICompatAdapter` speaks any OpenAI-compatible chat completions API.
Three local backends were validated against an M-series MacBook.

## Ollama (recommended for diploma demo)

```bash
brew install ollama
ollama serve &
ollama pull qwen2.5:1.5b-instruct      # ~1.0 GB, fast on CPU/MPS
```

Wire the adapter through env:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_TARGET_PROFILE=ollama-qwen-1_5b
export OPENAI_MODEL_NAME=qwen2.5:1.5b-instruct
```

The shipped profile `ollama-qwen-1_5b` (in
`src/prompt_autoimprove/registry/profiles/`) is already tuned for this model:
32k context, 1k output tokens, ~800 ms p50 latency.

Smoke test:

```bash
uv run pai improve --prompt "Summarize this article" --profile ollama-qwen-1_5b
```

You should see the **Probation output** section render with a real model reply.

## LM Studio

```bash
lms get qwen2.5-1.5b-instruct
lms server start          # exposes OpenAI-compatible API on :1234
```

Same env wiring with `OPENAI_BASE_URL=http://localhost:1234/v1`.

## Hugging Face direct

Pull a small instruct model via the authenticated CLI:

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b
# OR a GGUF:
hf download bartowski/Qwen2.5-1.5B-Instruct-GGUF \
  qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/
```

Then point either `SafetensorsHFAdapter` (`uv add transformers torch`) or
`GGUFAdapter` (`uv add llama-cpp-python`) at the file. Both are heavier on
macOS than Ollama and only worth using if Ollama isn't an option.

## Verification

`tests/integration/test_ollama_probation.py` skips when nothing is listening
on `localhost:11434`, so the suite stays green in CI but exercises the full
adapter → orchestrator → probation path on a developer machine with Ollama
up. Run it explicitly with:

```bash
OLLAMA_HOST=localhost:11434 uv run pytest tests/integration/test_ollama_probation.py -v
```
