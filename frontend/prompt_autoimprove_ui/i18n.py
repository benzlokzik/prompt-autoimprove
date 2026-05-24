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
    "model_family": {"en": "Model family", "ru": "Семейство моделей"},
    "vision": {"en": "vision", "ru": "vision"},
    "complexity": {"en": "Complexity", "ru": "Сложность"},
    "llm_rewrite_candidate": {
        "en": "LLM rewrite candidate",
        "ru": "Кандидат от LLM-переписи",
    },
    "llm_rewrite_note": {
        "en": "The LLM produced this rewrite but the deterministic strategy scored higher.",
        "ru": "LLM переписал промпт, но детерминированная стратегия набрала больше баллов.",
    },
    "sensitive": {"en": "Sensitive", "ru": "Чувствительный"},
    "sensitive_note": {
        "en": "Keep routing on local models and skip the LLM rewrite for private content.",
        "ru": "Маршрутизировать только на локальные модели и пропустить LLM-переписывание.",
    },
    "use_this_prompt": {"en": "Use this prompt", "ru": "Использовать этот промпт"},
    "revisions": {"en": "Revisions", "ru": "Редакции"},
    "load_into_editor": {"en": "Load into editor", "ru": "Загрузить в редактор"},
    "loading": {"en": "Loading…", "ru": "Загрузка…"},
    "err_network": {
        "en": "Cannot reach the backend. Check that the API is running.",
        "ru": "Бэкенд недоступен. Проверьте, запущен ли API.",
    },
    "err_validation": {
        "en": "The request was rejected as invalid (422). Check the prompt and profile.",
        "ru": "Запрос отклонён как некорректный (422). Проверьте промпт и профиль.",
    },
    "err_rate_limit": {
        "en": "Rate limit reached (429). Wait a moment and try again.",
        "ru": "Превышен лимит запросов (429). Подождите и попробуйте снова.",
    },
    "err_unknown_profile": {
        "en": "The selected profile was not found (404).",
        "ru": "Выбранный профиль не найден (404).",
    },
    "err_server": {
        "en": "The backend hit an internal error (5xx). Try again later.",
        "ru": "Внутренняя ошибка бэкенда (5xx). Попробуйте позже.",
    },
    "err_generic": {
        "en": "Something went wrong. Please try again.",
        "ru": "Что-то пошло не так. Попробуйте снова.",
    },
    "err_bad_response": {
        "en": "Unexpected response from the server. Please try again.",
        "ru": "Неожиданный ответ сервера. Попробуйте снова.",
    },
    "add_image": {
        "en": "Drop an image or click to add",
        "ru": "Перетащите изображение или нажмите",
    },
    "image_experimental": {"en": "experimental", "ru": "экспериментально"},
    "image_note": {
        "en": "Image input is unstable — support varies by model and image format.",
        "ru": "Ввод изображений нестабилен — поддержка зависит от модели и формата.",
    },
    "image_too_large": {
        "en": "Image is too large (max 8 MB).",
        "ru": "Изображение слишком большое (макс. 8 МБ).",
    },
}


def t(key: str, language) -> rx.Var:
    """Return the translation for `key` selected by `language` (rx.Var or str)."""
    en = STRINGS[key]["en"]
    ru = STRINGS[key]["ru"]
    return rx.cond(language == "ru", ru, en)
