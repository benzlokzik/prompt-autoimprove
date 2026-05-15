# Запуск с локальной моделью

`OpenAICompatAdapter` работает с любым OpenAI-compatible chat completions API.
Проект проверялся с тремя локальными backend на M-series MacBook.

## Ollama

```bash
brew install ollama
ollama serve &
ollama pull qwen2.5:1.5b-instruct      # about 1.0 GB, fast on CPU/MPS
```

Подключите adapter через переменные окружения:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_TARGET_PROFILE=ollama-qwen-1_5b
export OPENAI_MODEL_NAME=qwen2.5:1.5b-instruct
```

Поставляемый профиль `ollama-qwen-1_5b` в
`src/prompt_autoimprove/registry/profiles/` настроен под эту модель: 32k
context, 1k output tokens и около 800 ms p50 latency.

Smoke test:

```bash
uv run pai improve --prompt "Summarize this article" --profile ollama-qwen-1_5b
```

Должен появиться раздел **Probation output** с реальным ответом модели.

## LM Studio

```bash
lms get qwen2.5-1.5b-instruct
lms server start          # exposes an OpenAI-compatible API on :1234
```

Используйте те же переменные окружения с
`OPENAI_BASE_URL=http://localhost:1234/v1`.

## Hugging Face direct

Загрузите небольшую instruct-модель через authenticated CLI:

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b
# OR a GGUF:
hf download bartowski/Qwen2.5-1.5B-Instruct-GGUF \
  qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/
```

Затем укажите файл в `SafetensorsHFAdapter` (`uv add transformers torch`) или
`GGUFAdapter` (`uv add llama-cpp-python`). Оба варианта тяжелее на macOS, чем
Ollama, и в основном полезны, когда нужен прямой контроль над загрузкой модели.

## Проверка

`tests/integration/test_ollama_probation.py` пропускается, если на
`localhost:11434` ничего не слушает, поэтому CI не зависит от Ollama, а
локальные запуски проверяют adapter, orchestrator и probation path.

```bash
OLLAMA_HOST=localhost:11434 uv run pytest tests/integration/test_ollama_probation.py -v
```
