"""In-memory storage for Hunter.io API results."""

from typing import Dict, List, Optional, cast, final

from hunter.types import DomainSearchResponseDict, FindResponseDict, StoredResult, VerifyResponseDict


def verification_key(email: str) -> str:
    """Build the storage key for an email verification result."""
    return f'verify:{email}'


def domain_search_key(domain: str) -> str:
    """Build the storage key for a domain search result."""
    return f'domain:{domain}'


def email_find_key(domain: str, first_name: str, last_name: str) -> str:
    """Build the storage key for an email finder result."""
    return f'find:{domain}:{first_name}:{last_name}'


@final
class HunterStorage:
    """In-memory dictionary storage for Hunter.io API results."""

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._store: Dict[str, StoredResult] = {}

    def create(self, key: str, record: StoredResult) -> None:
        """Store a new result. Raises KeyError if the key already exists."""
        if key in self._store:
            raise KeyError(key)
        self._store[key] = record

    def update(self, key: str, record: StoredResult) -> None:
        """Overwrite an existing result. Raises KeyError if the key is absent."""
        if key not in self._store:
            raise KeyError(key)
        self._store[key] = record

    def get(self, key: str) -> Optional[StoredResult]:
        """Return the stored result for a key, or None if absent."""
        return self._store.get(key)

    def delete(self, key: str) -> bool:
        """Delete a stored result. Return True if the key existed."""
        if key not in self._store:
            return False
        self._store.pop(key)
        return True

    def clear(self) -> None:
        """Remove all stored results."""
        self._store.clear()

    def all_keys(self) -> List[str]:
        """Return a snapshot list of all currently stored keys."""
        return list(self._store.keys())


def get_verification(storage: HunterStorage, email: str) -> Optional[VerifyResponseDict]:
    """Retrieve a typed verification result from storage."""
    record = storage.get(verification_key(email))
    if record is None:
        return None
    return cast(VerifyResponseDict, record)


def get_domain_search(storage: HunterStorage, domain: str) -> Optional[DomainSearchResponseDict]:
    """Retrieve a typed domain search result from storage."""
    record = storage.get(domain_search_key(domain))
    if record is None:
        return None
    return cast(DomainSearchResponseDict, record)


def get_find_result(
    storage: HunterStorage,
    domain: str,
    first_name: str,
    last_name: str,
) -> Optional[FindResponseDict]:
    """Retrieve a typed email finder result from storage."""
    record = storage.get(email_find_key(domain, first_name, last_name))
    if record is None:
        return None
    return cast(FindResponseDict, record)
