"""Unit tests for HunterService."""

from unittest.mock import MagicMock

import pytest

from hunter.exceptions import HunterAuthError, HunterNetworkError
from hunter.service import HunterService
from hunter.storage import HunterStorage, domain_search_key, email_find_key, verification_key
from hunter.types import DomainSearchResponseDict, FindResponseDict, VerifyResponseDict

_EMAIL = 'test@example.com'
_DOMAIN = 'example.com'
_FIRST = 'John'
_LAST = 'Doe'


class TestVerifyEmail:
    """Tests for HunterService.verify_email."""

    def test_calls_client_on_cache_miss(
        self,
        service: HunterService,
        mock_client: MagicMock,
        verify_response: VerifyResponseDict,
    ) -> None:
        """The API client is called when storage has no cached result."""
        mock_client.verify_email.return_value = verify_response
        service.verify_email(_EMAIL)
        mock_client.verify_email.assert_called_once_with(_EMAIL)

    def test_saves_result_to_storage_on_miss(
        self,
        service: HunterService,
        mock_client: MagicMock,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """A fresh API result is persisted to storage after fetching."""
        mock_client.verify_email.return_value = verify_response
        service.verify_email(_EMAIL)
        assert storage.get(verification_key(_EMAIL)) == verify_response

    def test_cache_hit_skips_client_call(
        self,
        service: HunterService,
        mock_client: MagicMock,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """The client is not called when a cached result exists."""
        storage.create(verification_key(_EMAIL), verify_response)
        response = service.verify_email(_EMAIL)
        mock_client.verify_email.assert_not_called()
        assert response == verify_response

    def test_propagates_auth_error(
        self,
        service: HunterService,
        mock_client: MagicMock,
    ) -> None:
        """Auth errors from the client propagate unmodified."""
        mock_client.verify_email.side_effect = HunterAuthError('bad key')
        with pytest.raises(HunterAuthError):
            service.verify_email(_EMAIL)


class TestSearchDomain:
    """Tests for HunterService.search_domain."""

    def test_calls_client_on_cache_miss(
        self,
        service: HunterService,
        mock_client: MagicMock,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """The API client is called when storage has no cached result."""
        mock_client.search_domain.return_value = domain_response
        service.search_domain(_DOMAIN)
        mock_client.search_domain.assert_called_once_with(_DOMAIN)

    def test_saves_result_to_storage_on_miss(
        self,
        service: HunterService,
        mock_client: MagicMock,
        storage: HunterStorage,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """A fresh API result is persisted to storage after fetching."""
        mock_client.search_domain.return_value = domain_response
        service.search_domain(_DOMAIN)
        assert storage.get(domain_search_key(_DOMAIN)) == domain_response

    def test_cache_hit_skips_client_call(
        self,
        service: HunterService,
        mock_client: MagicMock,
        storage: HunterStorage,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """The client is not called when a cached result exists."""
        storage.create(domain_search_key(_DOMAIN), domain_response)
        response = service.search_domain(_DOMAIN)
        mock_client.search_domain.assert_not_called()
        assert response == domain_response


class TestFindEmail:
    """Tests for HunterService.find_email."""

    def test_calls_client_on_cache_miss(
        self,
        service: HunterService,
        mock_client: MagicMock,
        find_response: FindResponseDict,
    ) -> None:
        """The API client is called when storage has no cached result."""
        mock_client.find_email.return_value = find_response
        service.find_email(_DOMAIN, _FIRST, _LAST)
        mock_client.find_email.assert_called_once_with(_DOMAIN, _FIRST, _LAST)

    def test_saves_result_to_storage_on_miss(
        self,
        service: HunterService,
        mock_client: MagicMock,
        storage: HunterStorage,
        find_response: FindResponseDict,
    ) -> None:
        """A fresh API result is persisted to storage after fetching."""
        mock_client.find_email.return_value = find_response
        service.find_email(_DOMAIN, _FIRST, _LAST)
        assert storage.get(email_find_key(_DOMAIN, _FIRST, _LAST)) == find_response

    def test_cache_hit_skips_client_call(
        self,
        service: HunterService,
        mock_client: MagicMock,
        storage: HunterStorage,
        find_response: FindResponseDict,
    ) -> None:
        """The client is not called when a cached result exists."""
        storage.create(email_find_key(_DOMAIN, _FIRST, _LAST), find_response)
        response = service.find_email(_DOMAIN, _FIRST, _LAST)
        mock_client.find_email.assert_not_called()
        assert response == find_response

    def test_propagates_network_error(
        self,
        service: HunterService,
        mock_client: MagicMock,
    ) -> None:
        """Network errors from the client propagate unmodified."""
        mock_client.find_email.side_effect = HunterNetworkError('timeout')
        with pytest.raises(HunterNetworkError):
            service.find_email(_DOMAIN, _FIRST, _LAST)
