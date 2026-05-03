"""Service layer that orchestrates API calls and result persistence."""

from typing import final

from hunter.client import HunterClient
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


@final
class HunterService:
    """Orchestrates Hunter.io API calls with read-through storage caching."""

    def __init__(self, client: HunterClient, storage: HunterStorage) -> None:
        """Initialize with an API client and a storage instance."""
        self._client = client
        self._storage = storage

    def verify_email(self, email: str) -> VerifyResponseDict:
        """Verify an email address, returning a cached result if available."""
        cached = get_verification(self._storage, email)
        if cached is not None:
            return cached
        fresh = self._client.verify_email(email)
        self._storage.create(verification_key(email), fresh)
        return fresh

    def search_domain(self, domain: str) -> DomainSearchResponseDict:
        """Search a domain for email addresses, returning a cached result if available."""
        cached = get_domain_search(self._storage, domain)
        if cached is not None:
            return cached
        fresh = self._client.search_domain(domain)
        self._storage.create(domain_search_key(domain), fresh)
        return fresh

    def find_email(self, domain: str, first_name: str, last_name: str) -> FindResponseDict:
        """Find an email address for a person, returning a cached result if available."""
        cached = get_find_result(self._storage, domain, first_name, last_name)
        if cached is not None:
            return cached
        fresh = self._client.find_email(domain, first_name, last_name)
        self._storage.create(email_find_key(domain, first_name, last_name), fresh)
        return fresh
