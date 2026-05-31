# CLI-ի օգտագործումը

`pai` հրամանն ամենաարագ եղանակն է բարելավման pipeline-ը տերմինալից փորձարկելու համար։

## Ցուցադրել պրոֆիլները

```bash
uv run pai profiles
```

Սա տպում է `src/prompt_autoimprove/registry/profiles/`-ից բեռնված պրոֆիլները։

## Բարելավել prompt-ը

```bash
uv run pai improve --prompt "Extract emails from this text" --profile claude-sonnet-4-6
```

Հրամանը տպում է ընտրված ստրատեգիան, թեկնածու prompt-ը, ինտեգրացված գնահատականը և բացատրությունը։

`pai` CLI-ն տերմինալի աջակցվող ինտերֆեյսն է և pipeline-ը կիսում է HTTP և gRPC սերվերների հետ։

## gRPC-ի գործարկում

```bash
uv run pai serve-grpc
```

Գործարկում է `AutoImproveService` gRPC սերվերը (պորտ 50051)՝ օգտագործելով նույն գործարկման միջավայրը, ինչ HTTP հավելվածը։ HTTP հավելվածն արդեն լռելյայն գործարկում է gRPC-ն պրոցեսի ներսում, ուստի սա միայն-gRPC կամ multi-worker տեղակայումների համար է։ Ներդրված սերվերն անջատելու համար օգտագործիր `PAI_API__GRPC_ENABLED=false`։

## Հաճախ կիրառվող flag-եր

| Flag | Default | Notes |
| --- | --- | --- |
| `--profile` | `qwen3-7b` | Ցանկացած պրոֆիլ `registry/profiles/*.yaml`-ից։ |
| `--locale` | unset | Պարտադրում է լեզվի հայտնաբերումը, օրինակ՝ `en` կամ `ru`։ |
| `--sensitive` | `false` | Սահմանափակում է երթուղավորումը միայն լոկալ պրոֆիլներով։ |

## Մոդելի կատարումը

CLI-ն աշխատում է միայն-բարելավման ռեժիմում, քանի դեռ ադապտեր միացված չէ `AutoImproveOrchestrator.adapters`-ին։ Կարգավորիր Anthropic, OpenAI-compatible, GGUF կամ HF ադապտերներ, երբ ուզում ես, որ ընտրված թեկնածուն կատարվի իրական մոդելի կողմից probation probe-ի ընթացքում։
