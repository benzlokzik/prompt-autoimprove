# Մոդերացիա

Ընտրովի spam/չարաշահման ազդանշանը գնահատում է մուտքային prompt-ները և արդյունքը փոխանցում անվտանգության մետրիկային։ Այն հիմնված է [`benzlokzik/spam-detector`][spam-detector]-ի վրա (BERT/`transformers` տարբերակը՝ `cointegrated/rubert-tiny2`-ից ֆայն-թյունինգ արված) և **լռելյայն անջատված** է։ Երբ անջատված է, կամ երբ կախվածությունը կամ մոդելը հասանելի չէ, pipeline-ը տալիս է բայթ առ բայթ նույն արդյունքը, ինչ առանց դրա կառուցված build-ը։

## Շրջանակ

- **Միայն ռուսերեն։** Ազդանշանն աշխատում է միայն այն դեպքում, երբ նորմալիզացված prompt-ը հայտնաբերվում է որպես ռուսերեն (`detect_language(...) == "ru"`)․ անգլերեն և այլ prompt-ները երբեք չեն գնահատվում։
- **Ընտրովի կախվածություն։** Մոդելը և դրա `torch`/`transformers` փաթեթը գտնվում են `moderation` կախվածությունների խմբում․ լռելյայն տեղադրումը դրանք չի քաշում։
- **Սահուն դեգրադացիա։** Import-ի, բեռնման կամ inference-ի ցանկացած ձախողում դեգրադում է չեզոք արդյունքի՝ ոչ դրոշակ, ոչ տուգանք։

## Միացնելը

Տեղադրեք խումբը և միացրեք ազդանշանը․

```bash
uv sync --group moderation
PAI_MODERATION_ENABLED=1 \
  uv run uvicorn prompt_autoimprove.api.http.app:app --port 8000
```

### Կարգավորում

Բոլոր կարգավորումներն օգտագործում են `PAI_MODERATION_` նախածանցը։

| Variable | Default | Իմաստ |
| --- | --- | --- |
| `PAI_MODERATION_ENABLED` | `false` | Կառուցում և կցում է spam-ի գնահատիչը։ |
| `PAI_MODERATION_HF_MODEL` | `cointegrated/rubert-tiny2` | Ֆայն-թյունինգ արված դասակարգչի Hugging Face repo id-ն (կամ լոկալ ուղին)։ |
| `PAI_MODERATION_THRESHOLD` | `0.8` | P(spam)-ի արժեքը, որից սկսած (ներառյալ) prompt-ը մերժվում է, երբ արգելափակումը միացված է։ |
| `PAI_MODERATION_WEIGHT` | `0.5` | Սահմանափակ գործակից, որով spam-ի գնահատականն իջեցնում է անվտանգության մետրիկան։ |
| `PAI_MODERATION_BLOCK` | `false` | Մերժել շեմին հավասար կամ դրանից բարձր prompt-ները՝ դրանք միայն տուգանելու փոխարեն։ |

## Ինչպես է գնահատականն օգտագործվում

Միացված լինելու դեպքում նորմալիզատորն ավելացնում է `spam:<score>` գրառում prompt-ի անվտանգության դրոշակներին, որտեղ `<score>`-ը `P(spam)`-ն է $[0, 1]$ միջակայքում։ Այնուհետև այդ դրոշակը․

- **իջեցնում է անվտանգության մետրիկան** $q_s$ սահմանափակ գործակցով՝ $q_s \leftarrow q_s \cdot (1 - w_m \cdot p)$, որտեղ մոդերացիայի կշիռն է $w_m =$ `PAI_MODERATION_WEIGHT`, իսկ $p$-ն՝ spam-ի գնահատականը․ և
- **ընտրովի կերպով մերժում է հարցումը** մինչև մոդելի որևէ կանչը, երբ `PAI_MODERATION_BLOCK=1` և $p \ge$ `PAI_MODERATION_THRESHOLD`, ինչը վերադարձվում է որպես HTTP `422`։

## Որտեղ է այն երևում

- **HTTP:** `POST /v1/improve`-ը վերադարձնում է prompt-ի `safety_flags`-ը՝ ներառյալ ցանկացած `spam:<score>` գրառում։
- **gRPC:** `Normalization.safety_flags`-ն արդեն կրում է դրոշակները հոսքով փոխանցված `normalized` հաղորդագրության մեջ։
- **Frontend:** թեկնածուի տեսքը ցույց է տալիս «Possible spam» պիտակը տոկոսով, երբ ազդանշանը գործարկվում է։

## Մոդերացիայի image-ի կառուցում

Մոդելի կշիռները ներբեռնվում են Hugging Face Hub-ից build-ի ժամանակ, որպեսզի image-ն լինի ինքնաբավ․

```bash
docker build \
  --build-arg INCLUDE_MODERATION=1 \
  --build-arg PAI_MODERATION_HF_MODEL=<your-hf-model> \
  -t prompt-autoimprove:moderation .
```

Բազային image-ը glibc Debian է (`python:3.13-slim`), քանի որ `torch`-ը musllinux wheels չի մատակարարում․ լռելյայն build-ը մնում է թեթև՝ առանց `torch`-ի։

[spam-detector]: https://github.com/benzlokzik/spam-detector
