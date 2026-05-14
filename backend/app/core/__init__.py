from app.core.config import settings


def get_cors_origins():
    return settings.ALLOWED_ORIGINS
