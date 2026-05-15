import reflex as rx

EXAMPLE_PROMPTS_EN: tuple[str, ...] = (
    "Summarize the key benefits of microservices in 3 bullet points",
    "Extract all email addresses and phone numbers from this customer note: "
    "alice@example.com called from +1 555 123 4567 about invoice #42.",
    "Explain how the integrated quality score is computed and weight each component.",
)

EXAMPLE_PROMPTS_RU: tuple[str, ...] = (
    "Резюмируй ключевые преимущества микросервисов в 3 пунктах",
    "Извлеки все email-адреса и номера телефонов из заметки: "
    "alice@example.com звонила с +7 999 123 45 67 по поводу счёта №42.",
    "Объясни, как считается интегральная оценка качества и какой вес у каждой компоненты.",
)

STRINGS: dict[str, dict[str, str]] = {
    "tagline": {
        "en": "Improve any prompt for any LLM",
        "ru": "Улучшаем промпт для любой LLM",
    },
    "docs": {"en": "Docs", "ru": "Документация"},
    "github": {"en": "GitHub", "ru": "GitHub"},
    "model_profile": {"en": "Model profile", "ru": "Модель"},
    "your_prompt": {"en": "Your prompt", "ru": "Ваш промпт"},
    "placeholder": {
        "en": (
            "Paste a prompt and we'll route it through normalization, "
            "six improvement strategies, scoring, routing, and a probation run."
        ),
        "ru": (
            "Вставь промпт — он пройдёт через нормализацию, "
            "шесть стратегий улучшения, скоринг, маршрутизацию и пробный запуск."
        ),
    },
    "try_one": {"en": "Try one:", "ru": "Попробуй:"},
    "routing_to": {"en": "Routing to ", "ru": "Маршрут на "},
    "improve_btn": {"en": "Improve prompt", "ru": "Улучшить"},
    "improving": {"en": "Improving…", "ru": "Улучшаем…"},
    "session": {"en": "session ", "ru": "сессия "},
    "pipeline": {"en": "Pipeline", "ru": "Пайплайн"},
    "running": {"en": "running", "ru": "идёт"},
    "done": {"en": "done", "ru": "готово"},
    "pipeline_empty": {
        "en": "Submit a prompt to watch the pipeline run live",
        "ru": "Отправь промпт — пайплайн запустится в реальном времени",
    },
    "improved_prompt": {"en": "Improved prompt", "ru": "Улучшенный промпт"},
    "improved_empty_title": {
        "en": "The improved prompt appears here",
        "ru": "Улучшенный промпт появится здесь",
    },
    "improved_empty_sub": {
        "en": "We'll show the candidate text, the picked strategy, and the model response.",
        "ru": "Покажем кандидат, выбранную стратегию и ответ модели.",
    },
    "probation": {"en": "Probation output", "ru": "Ответ модели"},
    "score": {"en": "Score", "ru": "Оценка"},
    "why_candidate": {"en": "Why this candidate", "ru": "Почему этот кандидат"},
    "history": {"en": "History", "ru": "История"},
    "runs": {"en": " runs", "ru": " запусков"},
    "search_session": {
        "en": "Session id or user ref",
        "ru": "ID сессии или пользователь",
    },
    "history_empty": {
        "en": "Submit a prompt with a session id to start a history.",
        "ru": "Отправь промпт с ID сессии — начнётся история.",
    },
    "prompt_empty_error": {"en": "Prompt is empty", "ru": "Промпт пустой"},
    "language": {"en": "EN", "ru": "RU"},
}


def t(key: str, language) -> rx.Var:
    """Return the translation for `key` selected by `language` (rx.Var or str)."""
    en = STRINGS[key]["en"]
    ru = STRINGS[key]["ru"]
    return rx.cond(language == "ru", ru, en)
