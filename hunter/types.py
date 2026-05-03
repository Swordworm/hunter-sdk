"""TypedDicts for Hunter.io API request and response structures."""

from typing import List, Optional, TypedDict, Union


class SourceDict(TypedDict):
    """A source where an email address was found."""

    domain: str
    uri: str
    extracted_on: str
    last_seen_on: str
    still_on_page: bool


class VerificationDict(TypedDict):
    """Email verification status and date."""

    date: Optional[str]
    status: str


class VerifyDataDict(TypedDict):
    """Data payload from the email verifier endpoint."""

    status: str
    result: str
    score: int
    email: str
    regexp: bool
    gibberish: bool
    disposable: bool
    webmail: bool
    mx_records: bool
    smtp_server: bool
    smtp_check: bool
    accept_all: bool
    block: bool
    sources: List[SourceDict]


class VerifyMetaParamsDict(TypedDict):
    """Meta parameters echoed back in a verification response."""

    email: str


class VerifyMetaDict(TypedDict):
    """Meta block in a verification response."""

    params: VerifyMetaParamsDict


class VerifyResponseDict(TypedDict):
    """Full response from the email verifier endpoint."""

    data: VerifyDataDict
    meta: VerifyMetaDict


class EmailEntryDict(TypedDict):
    """A single email entry returned by a domain search."""

    value: str
    type: str
    confidence: int
    first_name: Optional[str]
    last_name: Optional[str]
    position: Optional[str]
    seniority: Optional[str]
    department: Optional[str]
    linkedin: Optional[str]
    twitter: Optional[str]
    phone_number: Optional[str]
    sources: List[SourceDict]
    verification: VerificationDict


class DomainSearchDataDict(TypedDict):
    """Data payload from the domain search endpoint."""

    domain: str
    disposable: bool
    webmail: bool
    accept_all: bool
    pattern: str
    organization: str
    emails: List[EmailEntryDict]


class DomainSearchMetaParamsDict(TypedDict):
    """Search parameters echoed back in a domain search response."""

    domain: Optional[str]
    company: Optional[str]
    type: Optional[str]
    seniority: Optional[str]
    department: Optional[str]


class DomainSearchMetaDict(TypedDict):
    """Meta block in a domain search response."""

    results: int
    limit: int
    offset: int
    params: DomainSearchMetaParamsDict


class DomainSearchResponseDict(TypedDict):
    """Full response from the domain search endpoint."""

    data: DomainSearchDataDict
    meta: DomainSearchMetaDict


class FindDataDict(TypedDict):
    """Data payload from the email finder endpoint."""

    first_name: str
    last_name: str
    email: str
    score: int
    domain: str
    accept_all: bool
    company: str
    position: Optional[str]
    twitter: Optional[str]
    linkedin_url: Optional[str]
    phone_number: Optional[str]
    sources: List[SourceDict]
    verification: VerificationDict


class FindMetaParamsDict(TypedDict):
    """Search parameters echoed back in an email finder response."""

    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    domain: Optional[str]
    company: Optional[str]


class FindMetaDict(TypedDict):
    """Meta block in an email finder response."""

    params: FindMetaParamsDict


class FindResponseDict(TypedDict):
    """Full response from the email finder endpoint."""

    data: FindDataDict
    meta: FindMetaDict


StoredResult = Union[VerifyResponseDict, DomainSearchResponseDict, FindResponseDict]
