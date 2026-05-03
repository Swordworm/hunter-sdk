"""Unit tests for HunterStorage and key-builder functions."""

import pytest

from hunter.storage import (
    HunterStorage,
    domain_search_key,
    email_find_key,
    get_domain_search,
    get_find_result,
    get_verification,
    verification_key,
)
from hunter.types import DomainSearchResponseDict, FindResponseDict, VerifyResponseDict

_EMAIL = 'test@example.com'
_DOMAIN = 'example.com'
_FIRST = 'John'
_LAST = 'Doe'
_FIRST_ALT = 'Jane'


class TestKeyBuilders:
    """Tests for module-level key-builder functions."""

    def test_verification_key_format(self) -> None:
        """Verification key uses the verify: prefix."""
        assert verification_key(_EMAIL) == f'verify:{_EMAIL}'

    def test_domain_search_key_format(self) -> None:
        """Domain search key uses the domain: prefix."""
        assert domain_search_key(_DOMAIN) == f'domain:{_DOMAIN}'

    def test_email_find_key_format(self) -> None:
        """Email find key uses the find: prefix with all three segments."""
        assert email_find_key(_DOMAIN, _FIRST, _LAST) == f'find:{_DOMAIN}:{_FIRST}:{_LAST}'

    def test_find_keys_differ_by_first_name(self) -> None:
        """Two find keys with different first names are distinct."""
        assert email_find_key(_DOMAIN, _FIRST, _LAST) != email_find_key(_DOMAIN, _FIRST_ALT, _LAST)


class TestHunterStorageReadWrite:
    """Tests for create, update, and get operations."""

    def test_create_and_get_returns_record(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """A created record can be retrieved with the same key."""
        key = verification_key(_EMAIL)
        storage.create(key, verify_response)
        assert storage.get(key) == verify_response

    def test_create_raises_on_duplicate_key(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """Creating under an existing key raises KeyError."""
        key = verification_key(_EMAIL)
        storage.create(key, verify_response)
        with pytest.raises(KeyError):
            storage.create(key, verify_response)

    def test_update_replaces_existing_record(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """Updating under an existing key replaces the stored record."""
        key = 'shared-key'
        storage.create(key, verify_response)
        storage.update(key, domain_response)
        assert storage.get(key) == domain_response

    def test_update_raises_on_missing_key(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """Updating an absent key raises KeyError."""
        with pytest.raises(KeyError):
            storage.update('nonexistent', verify_response)

    def test_get_missing_key_returns_none(self, storage: HunterStorage) -> None:
        """Getting an absent key returns None without raising."""
        assert storage.get('nonexistent') is None


class TestHunterStorageDeleteClear:
    """Tests for delete and clear operations."""

    def test_delete_existing_key_returns_true(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """Deleting an existing key returns True and removes the record."""
        key = verification_key(_EMAIL)
        storage.create(key, verify_response)
        assert storage.delete(key) is True
        assert storage.get(key) is None

    def test_delete_missing_key_returns_false(self, storage: HunterStorage) -> None:
        """Deleting an absent key returns False without raising."""
        assert storage.delete('nonexistent') is False

    def test_clear_empties_store(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """After clear(), all_keys() returns an empty list."""
        storage.create(verification_key(_EMAIL), verify_response)
        storage.clear()
        assert storage.all_keys() == []

    def test_all_keys_lists_stored_keys(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """all_keys() returns exactly the keys that were created."""
        key_a = verification_key(_EMAIL)
        key_b = domain_search_key(_DOMAIN)
        storage.create(key_a, verify_response)
        storage.create(key_b, domain_response)
        assert set(storage.all_keys()) == {key_a, key_b}


class TestTypedAccessors:
    """Tests for the typed get_* helper functions."""

    def test_get_verification_hit(
        self,
        storage: HunterStorage,
        verify_response: VerifyResponseDict,
    ) -> None:
        """get_verification returns the stored response on a hit."""
        storage.create(verification_key(_EMAIL), verify_response)
        assert get_verification(storage, _EMAIL) == verify_response

    def test_get_verification_miss(self, storage: HunterStorage) -> None:
        """get_verification returns None when nothing is stored."""
        assert get_verification(storage, _EMAIL) is None

    def test_get_domain_search_hit(
        self,
        storage: HunterStorage,
        domain_response: DomainSearchResponseDict,
    ) -> None:
        """get_domain_search returns the stored response on a hit."""
        storage.create(domain_search_key(_DOMAIN), domain_response)
        assert get_domain_search(storage, _DOMAIN) == domain_response

    def test_get_domain_search_miss(self, storage: HunterStorage) -> None:
        """get_domain_search returns None when nothing is stored."""
        assert get_domain_search(storage, _DOMAIN) is None

    def test_get_find_result_hit(
        self,
        storage: HunterStorage,
        find_response: FindResponseDict,
    ) -> None:
        """get_find_result returns the stored response on a hit."""
        storage.create(email_find_key(_DOMAIN, _FIRST, _LAST), find_response)
        assert get_find_result(storage, _DOMAIN, _FIRST, _LAST) == find_response

    def test_get_find_result_miss(self, storage: HunterStorage) -> None:
        """get_find_result returns None when nothing is stored."""
        assert get_find_result(storage, _DOMAIN, _FIRST, _LAST) is None
