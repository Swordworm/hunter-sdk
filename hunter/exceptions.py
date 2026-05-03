"""Hunter.io SDK exception hierarchy."""

from typing import final

from hunter.constants import HTTP_NOT_FOUND, HTTP_TOO_MANY_REQUESTS, HTTP_UNAUTHORIZED


class HunterError(Exception):
    """Base exception for all Hunter.io SDK errors."""


class HunterAPIError(HunterError):
    """Raised when the API returns an unexpected HTTP error status."""

    def __init__(self, status_code: int, message: str) -> None:
        """Initialize with HTTP status code and error message."""
        super().__init__(message)
        self.status_code: int = status_code


@final
class HunterAuthError(HunterAPIError):
    """Raised when the API key is missing or invalid (HTTP 401)."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(HTTP_UNAUTHORIZED, message)


@final
class HunterNotFoundError(HunterAPIError):
    """Raised when the requested resource is not found (HTTP 404)."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(HTTP_NOT_FOUND, message)


@final
class HunterRateLimitError(HunterAPIError):
    """Raised when the API rate limit or usage quota is exceeded (HTTP 429)."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(HTTP_TOO_MANY_REQUESTS, message)


@final
class HunterNetworkError(HunterError):
    """Raised when a network-level failure prevents the API call."""
