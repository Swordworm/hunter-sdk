"""Unit tests for HunterClient."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import requests

from hunter.client import HunterClient
from hunter.constants import BASE_URL, DEFAULT_TIMEOUT, HTTP_NOT_FOUND, HTTP_TOO_MANY_REQUESTS, HTTP_UNAUTHORIZED
from hunter.exceptions import (
    HunterAPIError,
    HunterAuthError,
    HunterNetworkError,
    HunterNotFoundError,
    HunterRateLimitError,
)
from hunter.types import DomainSearchResponseDict, FindResponseDict, VerifyResponseDict

_API_KEY = 'test-api-key'
_EMAIL = 'test@example.com'
_DOMAIN = 'example.com'
_FIRST = 'John'
_LAST = 'Doe'
_HTTP_INTERNAL_ERROR = 500


def _make_mock_response(payload: Dict[str, Any]) -> MagicMock:
    """Create a mock requests.Response returning the given JSON payload."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def _make_http_error(status_code: int) -> requests.HTTPError:
    """Create a requests.HTTPError with the given status code."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    return requests.HTTPError(response=mock_resp)


class TestVerifyEmail:
    """Tests for HunterClient.verify_email."""

    @patch('hunter.client.requests.get')
    def test_returns_verify_response(
        self,
        mock_get: MagicMock,
        verify_response: VerifyResponseDict,
    ) -> None:
        """verify_email returns the parsed API response on success."""
        mock_get.return_value = _make_mock_response(verify_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        response = client.verify_email(_EMAIL)
        assert response == verify_response

    @patch('hunter.client.requests.get')
    def test_sends_email_param(self, mock_get: MagicMock, verify_response: VerifyResponseDict) -> None:
        """verify_email includes the email in the request params."""
        mock_get.return_value = _make_mock_response(verify_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        client.verify_email(_EMAIL)
        _, kwargs = mock_get.call_args
        assert kwargs['params']['email'] == _EMAIL

    @patch('hunter.client.requests.get')
    def test_correct_endpoint(self, mock_get: MagicMock, verify_response: VerifyResponseDict) -> None:
        """verify_email calls the /email-verifier endpoint."""
        mock_get.return_value = _make_mock_response(verify_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        client.verify_email(_EMAIL)
        args, _ = mock_get.call_args
        assert args[0] == f'{BASE_URL}/email-verifier'


class TestSearchDomain:
    """Tests for HunterClient.search_domain."""

    @patch('hunter.client.requests.get')
    def test_returns_domain_response(
        self,
        mock_get: MagicMock,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """search_domain returns the parsed API response on success."""
        mock_get.return_value = _make_mock_response(domain_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        response = client.search_domain(_DOMAIN)
        assert response == domain_response

    @patch('hunter.client.requests.get')
    def test_sends_domain_param(
        self,
        mock_get: MagicMock,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """search_domain includes the domain in the request params."""
        mock_get.return_value = _make_mock_response(domain_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        client.search_domain(_DOMAIN)
        _, kwargs = mock_get.call_args
        assert kwargs['params']['domain'] == _DOMAIN


class TestFindEmail:
    """Tests for HunterClient.find_email."""

    @patch('hunter.client.requests.get')
    def test_returns_find_response(
        self,
        mock_get: MagicMock,
        find_response: FindResponseDict,
    ) -> None:
        """find_email returns the parsed API response on success."""
        mock_get.return_value = _make_mock_response(find_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        response = client.find_email(_DOMAIN, _FIRST, _LAST)
        assert response == find_response

    @patch('hunter.client.requests.get')
    def test_sends_name_params(
        self,
        mock_get: MagicMock,
        find_response: FindResponseDict,
    ) -> None:
        """find_email includes domain, first_name, and last_name in params."""
        mock_get.return_value = _make_mock_response(find_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        client.find_email(_DOMAIN, _FIRST, _LAST)
        _, kwargs = mock_get.call_args
        assert kwargs['params']['first_name'] == _FIRST
        assert kwargs['params']['last_name'] == _LAST


class TestAuthentication:
    """Tests for API key transmission and timeout forwarding."""

    @patch('hunter.client.requests.get')
    def test_api_key_included_in_params(
        self,
        mock_get: MagicMock,
        verify_response: VerifyResponseDict,
    ) -> None:
        """Every request includes the api_key query parameter."""
        mock_get.return_value = _make_mock_response(verify_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        client.verify_email(_EMAIL)
        _, kwargs = mock_get.call_args
        assert kwargs['params']['api_key'] == _API_KEY

    @patch('hunter.client.requests.get')
    def test_timeout_forwarded(
        self,
        mock_get: MagicMock,
        verify_response: VerifyResponseDict,
    ) -> None:
        """The configured timeout is passed to requests.get."""
        mock_get.return_value = _make_mock_response(verify_response)  # type: ignore[arg-type]
        client = HunterClient(api_key=_API_KEY)
        client.verify_email(_EMAIL)
        _, kwargs = mock_get.call_args
        assert kwargs['timeout'] == DEFAULT_TIMEOUT


class TestErrorMapping:
    """Tests for HTTP error-to-exception mapping."""

    @patch('hunter.client.requests.get')
    def test_unauthorized_raises_auth_error(self, mock_get: MagicMock) -> None:
        """HTTP 401 is mapped to HunterAuthError."""
        mock_get.return_value.raise_for_status.side_effect = _make_http_error(HTTP_UNAUTHORIZED)
        client = HunterClient(api_key=_API_KEY)
        with pytest.raises(HunterAuthError):
            client.verify_email(_EMAIL)

    @patch('hunter.client.requests.get')
    def test_not_found_raises_not_found_error(self, mock_get: MagicMock) -> None:
        """HTTP 404 is mapped to HunterNotFoundError."""
        mock_get.return_value.raise_for_status.side_effect = _make_http_error(HTTP_NOT_FOUND)
        client = HunterClient(api_key=_API_KEY)
        with pytest.raises(HunterNotFoundError):
            client.verify_email(_EMAIL)

    @patch('hunter.client.requests.get')
    def test_rate_limit_raises_rate_limit_error(self, mock_get: MagicMock) -> None:
        """HTTP 429 is mapped to HunterRateLimitError."""
        mock_get.return_value.raise_for_status.side_effect = _make_http_error(HTTP_TOO_MANY_REQUESTS)
        client = HunterClient(api_key=_API_KEY)
        with pytest.raises(HunterRateLimitError):
            client.verify_email(_EMAIL)

    @patch('hunter.client.requests.get')
    def test_server_error_raises_api_error(self, mock_get: MagicMock) -> None:
        """HTTP 500 is mapped to HunterAPIError carrying the status code."""
        mock_get.return_value.raise_for_status.side_effect = _make_http_error(_HTTP_INTERNAL_ERROR)
        client = HunterClient(api_key=_API_KEY)
        with pytest.raises(HunterAPIError) as exc_info:
            client.verify_email(_EMAIL)
        assert exc_info.value.status_code == _HTTP_INTERNAL_ERROR

    @patch('hunter.client.requests.get')
    def test_connection_error_raises_network_error(self, mock_get: MagicMock) -> None:
        """requests.ConnectionError is mapped to HunterNetworkError."""
        mock_get.side_effect = requests.ConnectionError('unreachable')
        client = HunterClient(api_key=_API_KEY)
        with pytest.raises(HunterNetworkError):
            client.verify_email(_EMAIL)

    @patch('hunter.client.requests.get')
    def test_timeout_raises_network_error(self, mock_get: MagicMock) -> None:
        """requests.Timeout is mapped to HunterNetworkError."""
        mock_get.side_effect = requests.Timeout('timed out')
        client = HunterClient(api_key=_API_KEY)
        with pytest.raises(HunterNetworkError):
            client.verify_email(_EMAIL)
