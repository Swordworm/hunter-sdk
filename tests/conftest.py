"""Shared pytest fixtures for the Hunter.io SDK test suite."""

from typing import List
from unittest.mock import MagicMock

import pytest

from hunter.client import HunterClient
from hunter.service import HunterService
from hunter.storage import HunterStorage
from hunter.types import (
    DomainSearchDataDict,
    DomainSearchMetaDict,
    DomainSearchMetaParamsDict,
    DomainSearchResponseDict,
    FindDataDict,
    FindMetaDict,
    FindMetaParamsDict,
    FindResponseDict,
    SourceDict,
    VerificationDict,
    VerifyDataDict,
    VerifyMetaDict,
    VerifyMetaParamsDict,
    VerifyResponseDict,
)

_SAMPLE_EMAIL = 'test@example.com'
_SAMPLE_DOMAIN = 'example.com'
_SAMPLE_FIRST = 'John'
_SAMPLE_LAST = 'Doe'
_SAMPLE_SCORE = 84
_SAMPLE_CONFIDENCE = 72


@pytest.fixture
def storage() -> HunterStorage:
    """Return a fresh empty HunterStorage instance."""
    return HunterStorage()


@pytest.fixture
def mock_client() -> MagicMock:
    """Return a MagicMock configured with the HunterClient spec."""
    return MagicMock(spec=HunterClient)


@pytest.fixture
def service(mock_client: MagicMock, storage: HunterStorage) -> HunterService:
    """Return a HunterService wired with a mock client and real storage."""
    return HunterService(client=mock_client, storage=storage)


@pytest.fixture
def verification() -> VerificationDict:
    """Return a minimal VerificationDict."""
    return VerificationDict(date=None, status='valid')


@pytest.fixture
def verify_response(verification: VerificationDict) -> VerifyResponseDict:
    """Return a minimal sample email verification response."""
    sources: List[SourceDict] = []
    meta_params = VerifyMetaParamsDict(email=_SAMPLE_EMAIL)
    meta = VerifyMetaDict(params=meta_params)
    data = VerifyDataDict(
        status='valid',
        result='deliverable',
        score=_SAMPLE_SCORE,
        email=_SAMPLE_EMAIL,
        regexp=True,
        gibberish=False,
        disposable=False,
        webmail=False,
        mx_records=True,
        smtp_server=True,
        smtp_check=True,
        accept_all=False,
        block=False,
        sources=sources,
    )
    return VerifyResponseDict(data=data, meta=meta)


@pytest.fixture
def domain_response(verification: VerificationDict) -> DomainSearchResponseDict:
    """Return a minimal sample domain search response."""
    meta_params = DomainSearchMetaParamsDict(
        domain=_SAMPLE_DOMAIN,
        company=None,
        type=None,
        seniority=None,
        department=None,
    )
    meta = DomainSearchMetaDict(results=0, limit=10, offset=0, params=meta_params)
    data = DomainSearchDataDict(
        domain=_SAMPLE_DOMAIN,
        disposable=False,
        webmail=False,
        accept_all=False,
        pattern='{first}',
        organization='Example',
        emails=[],
    )
    return DomainSearchResponseDict(data=data, meta=meta)


@pytest.fixture
def find_response(verification: VerificationDict) -> FindResponseDict:
    """Return a minimal sample email finder response."""
    sources: List[SourceDict] = []
    meta_params = FindMetaParamsDict(
        first_name=_SAMPLE_FIRST,
        last_name=_SAMPLE_LAST,
        full_name=None,
        domain=_SAMPLE_DOMAIN,
        company=None,
    )
    meta = FindMetaDict(params=meta_params)
    data = FindDataDict(
        first_name=_SAMPLE_FIRST,
        last_name=_SAMPLE_LAST,
        email=_SAMPLE_EMAIL,
        score=_SAMPLE_SCORE,
        domain=_SAMPLE_DOMAIN,
        accept_all=False,
        company='Example',
        position=None,
        twitter=None,
        linkedin_url=None,
        phone_number=None,
        sources=sources,
        verification=verification,
    )
    return FindResponseDict(data=data, meta=meta)
