# prompt-autoimprove

<section class="pai-hero" markdown>
<p class="pai-kicker">Prompt-ի օպտիմիզացիայի pipeline</p>
<p class="pai-pron"><strong>prompt-autoimprove</strong> → <em>pai</em>, <code>/paɪ/</code> (ինչպես &ldquo;pie&rdquo;)</p>

`prompt-autoimprove`-ը բարելավում է չմշակված prompt-ները՝ նախքան դրանք կհասնեն թիրախային մոդելին։ Այն
նորմալացնում է մուտքը, ընտրում թեկնածու ստրատեգիաներ, գնահատում արդյունքները, երթուղավորում
հաղթողին, ըստ ցանկության գործարկում մոդելի «probation probe» և բացատրում որոշումը։

<p class="pai-lede">
Նախագիծը նախատեսված է լոկալ փորձերի, API-ով ապահովվող ծառայությունների և
կրկնելի գնահատման աշխատանքային հոսքերի համար, որտեղ prompt-ի յուրաքանչյուր վերանայում պետք է լինի հետագծելի։
</p>
</section>

## Pipeline

<div class="pai-pipeline" markdown>
<div class="pai-step" markdown>Նորմալացրու տեքստը, locale-ը, առաջադրանքի տեսակը, բացակայող պարամետրերը, PII-ն և անվտանգության դրոշները։</div>
<div class="pai-step" markdown>Գեներացրու թեկնածուներ առաջադրանքին տեղյակ ստրատեգիաներով։</div>
<div class="pai-step" markdown>Վալիդացրու կառուցվածքը, երկարությունը, հակասությունները և անվտանգության սահմանափակումները։</div>
<div class="pai-step" markdown>Գնահատիր թեկնածուներին ինտեգրված որակի բանաձևով։</div>
<div class="pai-step" markdown>Երթուղավորիր հաղթողին լոկալ կամ API-ով ապահովվող պրոֆիլ։</div>
<div class="pai-step" markdown>Բացատրիր հաղթող վերանայումը և պահպանիր գործարկումը։</div>
</div>

## Սկսիր այստեղից

<div class="pai-links" markdown>

[Architecture](architecture.md){ .md-button }
[CLI](cli.md){ .md-button }
[Scoring](scoring.md){ .md-button }
[Local models](local-models.md){ .md-button }

</div>

## Հնարավորություններ

<div class="pai-grid" markdown>
<div class="pai-card" markdown>

### CLI

Գործարկիր `pai improve` լոկալ prompt-ի բարելավման համար և ստուգիր ընտրված
ստրատեգիան, գնահատականը և բացատրությունը։

</div>

<div class="pai-card" markdown>

### API

Օգտագործիր FastAPI HTTP backend-ը, SSE pipeline-ի հոսքը `/v1/improve/stream`-ում կամ gRPC `AutoImproveService`-ը։

</div>

<div class="pai-card" markdown>

### Frontend

Կառավարիր pipeline-ը Reflex վեբ կլիենտից՝ պրոֆիլի ընտրությամբ, փուլերի կենդանի թարմացումներով, գնահատման մանրամասներով և պատմությամբ։

</div>

<div class="pai-card" markdown>

### Գնահատում

Համեմատիր վերանայումները կշռված գումարով՝ $S = \sum_i w_i\,q_i$։ Տես
[Scoring](scoring.md)՝ ամբողջական բանաձևի և կշիռների համար։

</div>

<div class="pai-card" markdown>

### Լոկալ մոդելներ

Երթուղավորիր դեպի Ollama, LM Studio, լոկալ GGUF, Hugging Face safetensors կամ OpenAI-compatible endpoints։

</div>
</div>

## Արագ սկիզբ

```bash
uv sync --all-groups
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Մշակիր փաստաթղթերը

```bash
uv run mkdocs serve   # live preview at http://127.0.0.1:8000
uv run mkdocs build   # static site in ./site
```
