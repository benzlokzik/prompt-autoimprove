import hmac

from fastapi import Header, HTTPException, status

from prompt_autoimprove.config import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    expected = get_settings().api.api_key
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")
    return x_api_key
