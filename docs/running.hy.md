# Ծառայության գործարկում

Այս էջը նկարագրում է `prompt-autoimprove`-ի գործարկումը սկզբից մինչև վերջ — Docker Compose-ով՝ ամբողջ stack-ի համար, կամ լոկալ՝ մշակման համար։

## Docker Compose-ով

```bash
docker compose up -d --build app
```

Compose-ը գործարկում է կախվածությունները հերթականությամբ և սպասում, որ յուրաքանչյուրը դառնա healthy.

1. **postgres** — հավելվածի տվյալների բազա։
2. **redpanda** — Kafka-ի հետ համատեղելի իրադարձությունների broker։
3. **migrate** — մեկանգամյա job, որը կատարում է `alembic upgrade head`, ապա ավարտվում։ Հավելվածը **չի** գործարկվում, քանի դեռ միգրացիաները հաջողությամբ չեն ավարտվել։
4. **app** — FastAPI HTTP API `:8000`-ի վրա և gRPC `AutoImproveService` `:50051`-ի վրա՝ նույն պրոցեսում։

Web-կլիենտը (կառուցված `reflex --env prod`-ով) բարձրացրու առանձին.

```bash
docker compose up -d --build frontend   # http://localhost:3000
```

`minio`-ն ներառված է artifact-ների պահպանման համար, սակայն ոչինչ նրանից կախված չէ։ Ստուգիր պատրաստությունը.

```bash
curl http://localhost:8000/healthz
# {"status":"ok","orchestrator":true,"persistence":true}
```

| Service | Port(s) | Notes |
| --- | --- | --- |
| app (HTTP) | 8000 | `/docs`, `/healthz`, `/v1/*` |
| app (gRPC) | 50051 | `AutoImproveService`; անջատելու համար՝ `PAI_API__GRPC_ENABLED=false` |
| frontend | 3000 | Reflex UI (state backend 8001-ի վրա) |
| postgres | 5432 | |
| redpanda | 19092 | արտաքին Kafka listener |
| minio | 9000 / 9001 | API / console |

Քանդիր (ջնջիր volume-ները՝ տվյալների բազան զրոյացնելու համար).

```bash
docker compose down -v
```

## Հրապարակված պատկերներ

GitHub release-ի հրապարակումը կառուցում և push է անում երկու պատկերներն էլ GitHub Container Registry (`Publish images` workflow-ի միջոցով)՝ պիտակավորված release-ի տարբերակով (`X.Y.Z`, `X.Y`) և `latest`-ով.

```bash
docker pull ghcr.io/benzlokzik-university/prompt-autoimprove:latest
docker pull ghcr.io/benzlokzik-university/prompt-autoimprove-frontend:latest
```

Compose-ը հրապարակված պատկերի վրա ուղղորդելու համար՝ լոկալ կառուցելու փոխարեն, վերասահմանիր `image:`-ը (և հեռացրու `build:`-ը), կամ ուղղակիորեն `docker run` արա այն նույն `PAI_*` միջավայրով, ինչ `app` ծառայությունը։

## Լոկալ (առանց Docker-ի)

```bash
uv sync
uv run alembic upgrade head            # or set PAI_DB__AUTO_CREATE=1 for a throwaway DB
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000
```

Մյուս մուտքի կետերը կիսում են նույն pipeline-ի գործարկման միջավայրը.

```bash
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b   # CLI
uv run pai serve-grpc                                                # gRPC only
uv run pai profiles                                                  # list profiles
```

Տվյալների բազան ընտրովի է HTTP/CLI-ի հիմնական սցենարի համար — առանց դրա ծառայությունն աշխատում է միայն բարելավման ռեժիմում, և պատմությունը չի պահպանվում (`/healthz`-ը հաղորդում է `persistence: false`)։

## pixi-ով

[pixi](https://pixi.sh)-ն կառավարում է conda-forge-ի գործիքակազմը և PyPI փաթեթները նույն `pyproject.toml`-ից։ Այն հարմար է, երբ ուզում ես `llama-cpp-python`-ի համար native build գործիքները (C/C++ կոմպիլյատորը, CMake-ը, Ninja-ն և Make-ը մատակարարվում են `local-models` միջավայրի հետ)՝ առանց դրանք ձեռքով տեղադրելու։

```bash
# resolve + install the default environment
pixi install
pixi run pai improve --prompt "Summarize this PR" --profile qwen3-7b

# drop into a shell with the dev tools
pixi shell -e dev
```

Կախվածությունների յուրաքանչյուր խումբ համապատասխանում է մեկ pixi միջավայրի, և բոլորը կիսում են մեկ solve group, որպեսզի տարբերակները մնան համահունչ.

| Environment | Adds | Example |
| --- | --- | --- |
| `default` | միայն գործարկման միջավայր | `pixi run pai profiles` |
| `dev` | ruff, ty, pytest, prek, mkdocs | `pixi run -e dev pytest -q` |
| `frontend` | Reflex | `pixi run -e frontend reflex run` |
| `ml` | torch, transformers, tiktoken | `pixi run -e ml pai improve …` |
| `local-models` | llama-cpp-python + C/C++ գործիքակազմ | `pixi run -e local-models pai improve …` |
| `moderation` | spam-detector stack | `pixi run -e moderation uvicorn …` |

## Կարգավորումներ

Ծառայության բոլոր կարգավորումներն օգտագործում են `PAI_*` նախածանցը՝ `__`-ով որպես ներդրված բաժանարար։

| Variable | Default | Purpose |
| --- | --- | --- |
| `PAI_API__API_KEY` | `dev-key` in dev | Պարտադիր է dev-ից դուրս, եթե `PAI_API__ALLOW_DEV_KEY=1` դրված չէ։ |
| `PAI_API__GRPC_ENABLED` | `true` | Գործարկում է in-process gRPC սերվերը։ |
| `PAI_API__CORS_ORIGINS` | localhost:3000 | Ստորակետով բաժանված թույլատրված origin-ներ։ |
| `PAI_DB__DSN` | local Postgres | SQLAlchemy async DSN։ |
| `PAI_DB__AUTO_CREATE` | `false` | Բեռնման ժամանակ ստեղծել աղյուսակները՝ միգրացիաների փոխարեն (միայն dev-ի համար)։ |
| `PAI_KAFKA__ENABLED` | `false` | Հրապարակել pipeline-ի իրադարձությունները Kafka/Redpanda-ում։ |
| `PAI_CLASSIFIER__BACKEND` | `heuristic` | `heuristic`, `embeddings`, `judge`, կամ `composite`։ |
| `PAI_SCORER__SEMANTIC` | `false` | Խառնել embedding-ի մտադրության նմանությունը գնահատման մեջ (պահանջում է `ml` խումբը)։ |

## Ընտրովի կախվածությունների խմբեր

```bash
uv sync --group ml             # tiktoken tokenizer, embeddings, semantic scorer
uv sync --group local-models   # llama.cpp / GGUF local inference
uv sync --group frontend       # Reflex web client
```

Docker պատկերն ընդունում է `--build-arg INCLUDE_ML=1` և `--build-arg INCLUDE_LOCAL_MODELS=1`՝ դրանք ներդնելու համար։
