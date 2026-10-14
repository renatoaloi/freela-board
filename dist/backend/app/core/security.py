import re

from app.core.config import settings


def verify_api_key(api_key: str) -> bool:
    return api_key == settings.API_KEY


def validate_cnpj(cnpj: str) -> bool:
    if not cnpj or not isinstance(cnpj, str):
        return False
    cleaned = re.sub(r"\D", "", cnpj)
    if len(cleaned) != 14:
        return False
    if cleaned == cleaned[0] * 14:
        return False
    return True
