"""HTTP client for the Hunter.io API."""

from typing import Any, Dict, cast, final

import requests

from hunter.constants import BASE_URL, DEFAULT_TIMEOUT, HTTP_NOT_FOUND, HTTP_TOO_MANY_REQUESTS, HTTP_UNAUTHORIZED
from hunter.exceptions import (
    HunterAPIError,
    HunterAuthError,
    HunterNetworkError,
    HunterNotFoundError,
    HunterRateLimitError,
)
from hunter.types import DomainSearchResponseDict, FindResponseDict, VerifyResponseDict


def _map_http_error(exc: requests.HTTPError) -> HunterAPIError:
    """Map an HTTPError to the appropriate HunterAPIError subclass."""
    http_response = exc.response
    status = 0 if http_response is None else http_response.status_code
    message = str(exc)
    if status == HTTP_UNAUTHORIZED:
        return HunterAuthError(message)
    if status == HTTP_NOT_FOUND:
        return HunterNotFoundError(message)
    if status == HTTP_TOO_MANY_REQUESTS:
        return HunterRateLimitError(message)
    return HunterAPIError(status, message)


@final
class HunterClient:
    """Thin HTTP wrapper around the Hunter.io v2 REST API."""

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Initialize the client with an API key and optional timeout."""
        self._api_key = api_key
        self._timeout = timeout

    def verify_email(self, email: str) -> VerifyResponseDict:
        """Verify the deliverability of an email address."""
        return cast(
            VerifyResponseDict,
            self._get('/email-verifier', {'email': email}),
        )

    def search_domain(self, domain: str) -> DomainSearchResponseDict:
        """Return all email addresses found for a given domain."""
        return cast(
            DomainSearchResponseDict,
            self._get('/domain-search', {'domain': domain}),
        )

    def find_email(self, domain: str, first_name: str, last_name: str) -> FindResponseDict:
        """Find the most likely email address for a person at a domain."""
        return cast(
            FindResponseDict,
            self._get('/email-finder', {
                'domain': domain,
                'first_name': first_name,
                'last_name': last_name,
            }),
        )

    def _get(self, path: str, query_params: Dict[str, str]) -> Dict[str, Any]:
        """Send an authenticated GET request and return parsed JSON."""
        url = f'{BASE_URL}{path}'
        merged = {**query_params, 'api_key': self._api_key}
        try:
            response = requests.get(url, params=merged, timeout=self._timeout)
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise HunterNetworkError(str(exc)) from exc
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise _map_http_error(exc) from exc
        return cast(Dict[str, Any], response.json())
