# Запуск с локальной моделью

`OpenAICompatAdapter` работает с любым OpenAI-compatible chat completions API.
Проект был проверен с тремя локальными backend на MacBook серии M.

## Ollama

```bash
brew install ollama
ollama serve &
ollama pull qwen2.5:1.5b-instruct      # около 1.0 GB, быстро на CPU/MPS
```

Подключите адаптер через переменные окружения:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_TARGET_PROFILE=ollama-qwen-1_5b
export OPENAI_MODEL_NAME=qwen2.5:1.5b-instruct
```

Поставляемый профиль `ollama-qwen-1_5b` в
`src/prompt_autoimprove/registry/profiles/` настроен для этой модели: контекст
32k, 1k output tokens и p50 latency около 800 ms.

Smoke test:

```bash
uv run pai improve --prompt "Summarize this article" --profile ollama-qwen-1_5b
```

Вы должны увидеть раздел **Probation output** с реальным ответом модели.

## LM Studio

```bash
lms get qwen2.5-1.5b-instruct
lms server start          # открывает OpenAI-compatible API на :1234
```

Используйте ту же настройку через переменные окружения с
`OPENAI_BASE_URL=http://localhost:1234/v1`.

## Hugging Face direct

Скачайте небольшую instruct-модель через аутентифицированный CLI:

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b
# OR a GGUF:
hf download bartowski/Qwen2.5-1.5B-Instruct-GGUF \
  qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/
```

Затем укажите путь к файлу либо для `SafetensorsHFAdapter` (`uv add transformers torch`), либо для `GGUFAdapter` (`uv add llama-cpp-python`). Оба варианта тяжелее на macOS, чем Ollama, и в
основном полезны, когда нужен прямой контроль над загрузкой модели.

## Backend'ы классификатора сложности

Оркестратор решает, нужно ли передавать промпт в LLM rewriter, используя
`ComplexityClassifier`. Выберите один через `PAI_CLASSIFIER__BACKEND`:

| Backend | Что делает | Стоимость / задержка | Когда использовать |
| --- | --- | --- | --- |
| `heuristic` (по умолчанию) | Чистые Python-правила по длине, задаче, параметрам и неоднозначности. | ~µs, ноль зависимостей. | Вариант по умолчанию для production. |
| `embeddings` | Cosine similarity к подготовленным simple/hard centroids через `sentence-transformers/all-MiniLM-L6-v2`. | ~10 ms после прогрева; нужен `uv sync --group ml`. | Когда вам нужно ML quality без стоимости на каждый вызов. |
| `judge` | Отправляет однословную оценку "simple/hard" в настроенный `ModelAdapter` для improvement. Кэшируется по хэшу промпта. | Один небольшой LLM-вызов на каждый некэшированный промпт. | Максимальное качество, предсказуемый бюджет. |
| `composite` | Сначала heuristic; обращается к embedding backend только когда heuristic score попадает в `[composite_lo, composite_hi]`. | В основном бесплатно, ML на пограничных случаях. | Рекомендуется, когда у вас установлен `ml` group. |

Другие настройки: `PAI_CLASSIFIER__EMBEDDING_MODEL`,
`PAI_CLASSIFIER__DEVICE`, `PAI_CLASSIFIER__COMPOSITE_LO`,
`PAI_CLASSIFIER__COMPOSITE_HI`.

## Проверка

`tests/integration/test_ollama_probation.py` пропускается, если на
`localhost:11434` ничего не слушает, поэтому CI остается независимым от
Ollama, а локальные запуски могут проверять адаптер, оркестратор и probation
path.

```bash
OLLAMA_HOST=localhost:11434 uv run pytest tests/integration/test_ollama_probation.py -v
```

Хелпер `scripts/local_e2e.py` прогоняет полный pipeline classifier +
rewriter с любым локальным тегом Ollama и печатает как переписанный кандидат,
так и финально выбранный промпт:

```bash
uv run python scripts/local_e2e.py ollama-qwen3-1_7b qwen3:1.7b
```
