"""Hunter.io SDK constants."""

from typing import Final

BASE_URL: Final[str] = 'https://api.hunter.io/v2'
DEFAULT_TIMEOUT: Final[int] = 30

HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_NOT_FOUND: Final[int] = 404
HTTP_TOO_MANY_REQUESTS: Final[int] = 429
