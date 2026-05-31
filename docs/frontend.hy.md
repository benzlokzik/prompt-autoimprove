# Frontend

web client-ը գտնվում է `frontend/` պանակում և կառուցված է
[Reflex](https://reflex.dev)-ի վրա։ Reflex-ը կոմպիլացնում է Python-ով գրված UI-ի
սահմանումը Next.js, React, Tailwind և Radix Themes app-ի մեջ։ Բրաուզերի և սերվերի
վիճակների սինխրոնիզացիան իրականացվում է WebSocket-ով, իսկ pipeline-ի
իրադարձությունները հոսքով փոխանցվում են FastAPI backend-ից Server-Sent Events-ի
միջոցով՝ `/v1/improve/stream` հասցեով։

## Կառուցվածք

```text
frontend/
├── rxconfig.py                        # api_url + port config
├── Dockerfile                         # multi-stage build with uv
└── prompt_autoimprove_ui/
    ├── prompt_autoimprove_ui.py       # rx.App + theme
    ├── state.py                       # PipelineState stages, metrics, history
    ├── api_client.py                  # httpx wrapper for SSE events
    ├── pages/home.py                  # main workspace layout
    └── components/
        ├── header.py
        ├── profile_picker.py
        ├── prompt_card.py
        ├── pipeline_timeline.py
        ├── candidate_view.py
        ├── metric_breakdown.py
        ├── explanation_card.py
        └── history_panel.py
```

## Լոկալ գործարկում

```bash
# 1. start the FastAPI backend on port 8000
uv run uvicorn prompt_autoimprove.api.http.app:app --port 8000

# 2. in another shell, start the Reflex dev server
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Բացեք <http://localhost:3000>։ Ձախ վահանակում ցուցադրվում են մոդելների
պրոֆիլները, որոնք բերվում են `/v1/profiles`-ից։ Ընտրեք պրոֆիլ, փակցրեք prompt-ը և
սեղմեք **Բարելավել**։ pipeline-ի ժամանակագիծը լրացվում է փուլ առ փուլ, իսկ
մետրիկաների բաժանումն ու բացատրության քարտը թարմացվում են, երբ գնահատումն
ավարտվում է։ Եթե backend-ում կարգավորված են `ANTHROPIC_API_KEY`-ը կամ `OPENAI_*`
փոփոխականները, ընտրված թեկնածուն կարող է անցնել նաև իրական մոդելի փորձաշրջանի
ստուգում և ցույց տալ արդյունքը բարելավված prompt-ի վահանակում։

## Աշխատանքային տարածքի հնարավորությունները

- prompt-ի քարտի վրա գտնվող **Զգայուն** փոխարկիչը սահմանում է `sensitive`, ինչը
  երթուղավորումը պահում է լոկալ մոդելների վրա և բաց է թողնում LLM-ով
  վերաշարադրումը. ակտիվ UI-ի լեզուն ուղարկվում է որպես `locale_hint`։
- **Պատկերների ներմուծում (փորձարարական)։** Քաշեք կամ ընտրեք պատկերներ prompt-ի
  քարտի վրա։ Դրանք ներդրվում են որպես base64 data URIs և ուղարկվում որպես
  `attachments` դեպի `POST /v1/improve` vision-ի աջակցությամբ պրոֆիլների համար։
  Աջակցությունն անկայուն է և տարբերվում է ըստ մոդելի և պատկերի ֆորմատի.
  առավելագույնը՝ 4 պատկեր, յուրաքանչյուրը՝ 8 MB։
- **Օգտագործել այս prompt-ը**՝ պատճենում է բարելավված թեկնածուն հետ՝ խմբագրիչ։
- **Պատմության խորացված դիտում։** Պատմության տողերը բացվում են՝ ցուցադրելով անցյալ
  վերանայումները. յուրաքանչյուր վերանայում կարելի է հետ բեռնել խմբագրիչ։
- **Տարբերակված սխալներ։** Ցանցի, վալիդացիայի (422), rate-limit-ի (429),
  չգտնվածի (404) և սերվերի (5xx) ձախողումները ցույց են տալիս տարբեր
  հաղորդագրություններ։
- Մետրիկաների ցանցը իր սյունակների քանակը ստանում է վերադարձված մետրիկաներից և
  հարմարվում է փոքր էկրաններին։

## Միջավայր

| Variable | Default | Նշանակություն |
| --- | --- | --- |
| `PAI_BACKEND_URL` | `http://localhost:8000` | backend-ի բազային URL, որը կանչվում է SPA-ի կողմից։ |
| `PAI_API_KEY` | `dev-key` | Ուղարկվում է որպես `x-api-key` յուրաքանչյուր հարցմամբ։ |
| `PAI_FRONTEND_PORT` | `3000` | Reflex-ի dev սերվերի port-ը։ |
| `PAI_FRONTEND_BACKEND_PORT` | `8001` | Reflex-ի ներքին WebSocket port-ը։ |

## Docker

`docker compose --profile app up --build` հրամանը գործարկում է `postgres`-ը,
`redpanda`-ն, `minio`-ն, FastAPI `app`-ը `8000` և `50051` port-երի վրա և Reflex
`frontend`-ը `3000` և `8001` port-երի վրա։ frontend-ի image-ը կառուցվում է
`frontend/Dockerfile`-ից՝ `frontend` կախվածությունների խմբով նույն `uv.lock`-ից։
