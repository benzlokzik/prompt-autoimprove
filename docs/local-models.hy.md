# Աշխատանք լոկալ մոդելի հետ

`OpenAICompatAdapter`-ը աշխատում է ցանկացած OpenAI-compatible chat completions API-ի հետ։ Նախագիծը ստուգվել է երեք լոկալ backend-ի վրա՝ M-series MacBook-ի վրա։

## Ollama

```bash
brew install ollama
ollama serve &
ollama pull qwen2.5:1.5b-instruct      # about 1.0 GB, fast on CPU/MPS
```

Միացրու ադապտերը միջավայրի փոփոխականների միջոցով․

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_TARGET_PROFILE=ollama-qwen-1_5b
export OPENAI_MODEL_NAME=qwen2.5:1.5b-instruct
```

`src/prompt_autoimprove/registry/profiles/`-ում տրամադրված `ollama-qwen-1_5b` պրոֆիլը կարգավորված է հենց այս մոդելի համար՝ 32k կոնտեքստ, 1k ելքային token-ներ և մոտ 800 ms p50 լատենտություն։

Smoke test․

```bash
uv run pai improve --prompt "Summarize this article" --profile ollama-qwen-1_5b
```

Պետք է տեսնես **Probation output** բաժինը՝ մոդելի իրական պատասխանով։

## LM Studio

```bash
lms get qwen2.5-1.5b-instruct
lms server start          # exposes an OpenAI-compatible API on :1234
```

Օգտագործիր նույն միջավայրի կարգավորումը՝ `OPENAI_BASE_URL=http://localhost:1234/v1`։

## Hugging Face ուղղակիորեն

Ներբեռնիր փոքր instruct մոդել նույնականացված CLI-ով․

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b
# OR a GGUF:
hf download bartowski/Qwen2.5-1.5B-Instruct-GGUF \
  qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/
```

Հետո ուղղորդիր ֆայլին կա՛մ `SafetensorsHFAdapter`-ը (`uv add transformers torch`), կա՛մ `GGUFAdapter`-ը (`uv add llama-cpp-python`)։ Երկու տարբերակն էլ macOS-ի վրա ավելի ծանր են, քան Ollama-ն, և հիմնականում օգտակար են, երբ քեզ պետք է մոդելի բեռնման ուղղակի վերահսկողություն։

## Բարդության դասակարգիչի backend-ներ

Օրկեստրատորը որոշում է՝ արդյոք էսկալացնել prompt-ը LLM rewriter-ին՝ օգտագործելով `ComplexityClassifier`։ Ընտրիր մեկը `PAI_CLASSIFIER__BACKEND`-ի միջոցով․

| Backend | Ի՞նչ է անում | Արժեք / լատենտություն | Ե՞րբ օգտագործել |
|---|---|---|---|
| `heuristic` (լռելյայն) | Մաքուր Python կանոններ՝ երկարության, task-ի, պարամետրերի և երկիմաստության հիման վրա։ | ~µs, զրո կախվածություն։ | Production-ի լռելյայն։ |
| `embeddings` | Կոսինուսային նմանություն ընտրված պարզ/բարդ ցենտրոիդների հետ՝ `sentence-transformers/all-MiniLM-L6-v2`-ի միջոցով։ | ~10 ms՝ տաքացումից հետո; պահանջում է `uv sync --group ml`։ | Երբ ուզում ես ML որակ՝ առանց ամեն կանչի արժեքի։ |
| `judge` | Ուղարկում է մեկ բառանի «simple/hard» դատողություն կարգավորված improver `ModelAdapter`-ին։ Քեշավորված է ըստ prompt-ի hash-ի։ | Մեկ փոքր LLM կանչ՝ ամեն ոչ-քեշավորված prompt-ի համար։ | Ամենաբարձր որակ, կանխատեսելի բյուջե։ |
| `composite` | Սկզբում հյուրիստիկ; embedding backend-ին դիմում է միայն այն դեպքում, երբ հյուրիստիկ միավորն ընկնում է `[composite_lo, composite_hi]` միջակայք։ | Հիմնականում անվճար, ML՝ սահմանային դեպքերում։ | Խորհուրդ է տրվում, երբ տեղադրել ես `ml` group-ը։ |

Այլ կարգավորիչներ․ `PAI_CLASSIFIER__EMBEDDING_MODEL`, `PAI_CLASSIFIER__DEVICE`, `PAI_CLASSIFIER__COMPOSITE_LO`, `PAI_CLASSIFIER__COMPOSITE_HI`։

## Ստուգում

`tests/integration/test_ollama_probation.py`-ն բաց է թողնվում, երբ `localhost:11434`-ին ոչինչ չի լսում, այնպես որ CI-ն մնում է Ollama-ից անկախ, մինչդեռ լոկալ գործարկումները կարող են փորձարկել ադապտերը, օրկեստրատորը և probation-ի ուղին։

```bash
OLLAMA_HOST=localhost:11434 uv run pytest tests/integration/test_ollama_probation.py -v
```

`scripts/local_e2e.py` օժանդակ սկրիպտը գործարկում է ամբողջական դասակարգիչ + rewriter pipeline-ը ցանկացած լոկալ Ollama tag-ի դեմ և տպում է թե՛ վերաշարադրված թեկնածուն, թե՛ վերջնականապես ընտրված prompt-ը․

```bash
uv run python scripts/local_e2e.py ollama-qwen3-1_7b qwen3:1.7b
```
