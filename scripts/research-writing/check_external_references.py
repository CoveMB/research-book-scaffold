#!/usr/bin/env python3
"""Check external URLs, DOIs, and optional archive coverage conservatively."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths
from project_config import change_to_project_root
from script_utils import DEFAULT_IGNORED_DIRS, DOCUMENT_SUFFIXES, iter_supported_files, read_text, write_text_file

configure_script_paths(__file__)

DEFAULT_SCAN_ROOTS = [
    Path("bibliography/references.bib"),
    Path("notes"),
    Path("research"),
    Path("manuscript"),
]
SUPPORTED_SUFFIXES = set(DOCUMENT_SUFFIXES) | {".bib"}
IGNORED_DIRS = set(DEFAULT_IGNORED_DIRS)
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_DNS_ATTEMPTS = 3
DNS_RETRY_DELAY_SECONDS = 0.25
USER_AGENT = (
    "research-book-scaffold-external-reference-check/1.0 "
    "(+https://github.com/CoveMB/research-book-scaffold)"
)

URL_TOKEN_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)
TEXT_FIELD_RE = re.compile(r"^\s*[-*]?\s*([A-Za-z][A-Za-z0-9_-]*)\s*[:=]\s*(.+?)\s*$")
BIB_ENTRY_START_RE = re.compile(r"@\s*([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
BIB_FIELD_RE = re.compile(
    r"(?im)^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*"
    r"(\{(?:[^{}]|\{[^{}]*\})*\}|\"(?:[^\"\\]|\\.)*\"|[^,\n]+)\s*,?"
)
DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)

URL_FIELD_NAMES = {"url"}
ARCHIVE_URL_FIELD_NAMES = {"archive_url", "archiveurl"}
DOI_FIELD_NAMES = {"doi"}
ACCESS_DATE_FIELD_NAMES = {"access_date", "accessdate", "accessed", "urldate"}
ARCHIVE_HOSTS = {"archive.org", "web.archive.org"}
DOI_HOSTS = {"doi.org", "www.doi.org", "dx.doi.org"}
GET_FALLBACK_STATUS_CODES = {403, 405, 406, 429, 500, 501, 503}
WARNING_STATUS_CODES = {401, 402, 403, 407, 408, 425, 429, 451}
BROKEN_STATUS_CODES = {404, 410}
FAILING_CATEGORIES = {"broken", "malformed_doi", "malformed_url"}
CATEGORY_ORDER = ["ok", "warning", "broken", "missing_archive", "malformed_doi", "malformed_url"]
CATEGORY_LABELS = {
    "ok": "ok",
    "warning": "warning/unknown",
    "broken": "broken",
    "missing_archive": "missing archive",
    "malformed_doi": "malformed DOI",
    "malformed_url": "malformed URL",
}


class ReferenceCheckError(RuntimeError):
    """Base class for HTTP check failures that should be categorized."""


class TimeoutCheckError(ReferenceCheckError):
    """Raised when a request times out."""


class SslCheckError(ReferenceCheckError):
    """Raised when TLS validation prevents a reliable check."""


class DnsCheckError(ReferenceCheckError):
    """Raised when name resolution fails."""


class NetworkCheckError(ReferenceCheckError):
    """Raised for other network errors."""


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    url: str
    body: str = ""


@dataclass(frozen=True)
class Reference:
    kind: str
    target: str
    path: Path
    line_number: int
    entry_key: str | None = None
    has_archive: bool = False


@dataclass(frozen=True)
class Finding:
    category: str
    reference: Reference
    message: str
    checked_url: str | None = None
    status_code: int | None = None


class UrlLibHttpClient:
    def request(
        self,
        method: str,
        url: str,
        timeout: float,
        headers: dict[str, str],
    ) -> HttpResponse:
        request = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read(4096).decode("utf-8", errors="replace")
                return HttpResponse(response.status, response.geturl(), body)
        except urllib.error.HTTPError as error:
            body = error.read(4096).decode("utf-8", errors="replace")
            return HttpResponse(error.code, error.geturl(), body)
        except TimeoutError as error:
            raise TimeoutCheckError(str(error)) from error
        except urllib.error.URLError as error:
            raise classify_url_error(error) from error
        except ssl.SSLError as error:
            raise SslCheckError(str(error)) from error
        except OSError as error:
            raise NetworkCheckError(str(error)) from error


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional files or directories to scan. Defaults to bibliography/, notes/, research/, and manuscript/.",
    )
    parser.add_argument(
        "--check-archives",
        action="store_true",
        help=(
            "Query the Internet Archive availability endpoint for public URLs. "
            "This submits checked public URLs to archive.org but does not create snapshots."
        ),
    )
    parser.add_argument(
        "--create-archives",
        action="store_true",
        help=(
            "Request Internet Archive snapshots for missing public URLs. "
            "Privacy warning: this submits URLs to a public third-party service."
        ),
    )
    parser.add_argument(
        "--allow-private-archive-submission",
        action="store_true",
        help=(
            "Allow archive availability or snapshot requests for localhost, private IP, .local, "
            "or single-label hostnames. Use only when those URLs are safe to disclose."
        ),
    )
    parser.add_argument(
        "--allow-private-url-checks",
        action="store_true",
        help=(
            "Allow primary URL checks for localhost, private IP, .local, or single-label hostnames. "
            "Use only when probing those URLs is safe."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Per-request timeout in seconds. Default: {DEFAULT_TIMEOUT_SECONDS:g}.",
    )
    parser.add_argument(
        "--dns-attempts",
        type=int,
        default=DEFAULT_DNS_ATTEMPTS,
        help=f"DNS attempts before classifying name resolution as broken. Default: {DEFAULT_DNS_ATTEMPTS}.",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        help="Optional path for a JSON report, for example reports/external-reference-check.json.",
    )
    parser.add_argument(
        "--markdown-report",
        type=Path,
        help="Optional path for a Markdown report.",
    )
    parser.add_argument(
        "--show-ok",
        action="store_true",
        help="Print ok references as well as warnings and likely failures.",
    )
    return parser.parse_args(argv)


def classify_url_error(error: urllib.error.URLError) -> ReferenceCheckError:
    reason = error.reason
    if isinstance(reason, TimeoutError | socket.timeout):
        return TimeoutCheckError(str(reason))
    if isinstance(reason, ssl.SSLError):
        return SslCheckError(str(reason))
    if isinstance(reason, socket.gaierror):
        return DnsCheckError(str(reason))
    return NetworkCheckError(str(reason))


def normalize_bib_field_name(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def clean_bib_value(value: str) -> str:
    cleaned = value.strip().rstrip(",").strip()
    if len(cleaned) >= 2 and cleaned[0] == "{" and cleaned[-1] == "}":
        cleaned = cleaned[1:-1]
    elif len(cleaned) >= 2 and cleaned[0] == '"' and cleaned[-1] == '"':
        cleaned = cleaned[1:-1]
    return re.sub(r"\s+", " ", cleaned).strip()


def clean_url_token(raw_url: str) -> str:
    url = raw_url.strip()
    while url and url[-1] in ".,;:!?":
        url = url[:-1]
    while url and url[-1] in "\"]}'":
        url = url[:-1]
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def is_valid_url(url: str) -> bool:
    if any(character.isspace() for character in url):
        return False
    try:
        parsed = urllib.parse.urlsplit(url)
        parsed.port
    except ValueError:
        return False
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname)


def normalize_doi(raw_doi: str) -> str:
    doi = clean_url_token(raw_doi.strip().strip("{}\"'"))
    lowered = doi.lower()
    if lowered.startswith("doi:"):
        doi = doi[4:].strip()
        lowered = doi.lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/"):
        if lowered.startswith(prefix):
            doi = urllib.parse.unquote(doi[len(prefix) :])
            break
    return clean_url_token(doi.strip())


def is_valid_doi(doi: str) -> bool:
    return bool(DOI_RE.fullmatch(doi))


def doi_resolver_url(doi: str) -> str:
    return f"https://doi.org/{urllib.parse.quote(doi, safe='/._;():')}"


def url_hostname(url: str) -> str:
    try:
        return urllib.parse.urlsplit(url).hostname or ""
    except ValueError:
        return ""


def is_doi_url(url: str) -> bool:
    return url_hostname(url).lower() in DOI_HOSTS


def doi_from_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return normalize_doi(urllib.parse.unquote(parsed.path.lstrip("/")))


def is_archive_service_url(url: str) -> bool:
    return url_hostname(url).lower() in ARCHIVE_HOSTS


def original_url_from_archive_url(url: str) -> str | None:
    if url_hostname(url).lower() != "web.archive.org":
        return None
    try:
        path = urllib.parse.urlsplit(url).path
    except ValueError:
        return None
    match = re.match(r"^/web/[^/]+/(https?://.+)$", path)
    if not match:
        return None
    return clean_url_token(urllib.parse.unquote(match.group(1)))


def is_private_or_local_url(url: str) -> bool:
    host = url_hostname(url).lower()
    if not host:
        return True
    if host == "localhost" or host.endswith(".local") or "." not in host:
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local or address.is_reserved


def iter_bib_entries(text: str) -> list[tuple[str, int, str]]:
    entries: list[tuple[str, int, str]] = []
    for match in BIB_ENTRY_START_RE.finditer(text):
        entry_key = match.group(2).strip()
        opening_brace = text.find("{", match.start(), match.end())
        if opening_brace == -1:
            continue
        depth = 0
        closing_brace = None
        for index in range(opening_brace, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    closing_brace = index
                    break
        if closing_brace is None:
            continue
        entries.append((entry_key, opening_brace + 1, text[opening_brace + 1 : closing_brace]))
    return entries


def line_number_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def bib_fields(entry_text: str, entry_start: int, full_text: str) -> list[tuple[str, str, int]]:
    fields: list[tuple[str, str, int]] = []
    for match in BIB_FIELD_RE.finditer(entry_text):
        absolute_start = entry_start + match.start()
        fields.append(
            (
                normalize_bib_field_name(match.group(1)),
                clean_bib_value(match.group(2)),
                line_number_for_offset(full_text, absolute_start),
            )
        )
    return fields


def reference_from_url(path: Path, line_number: int, url: str, entry_key: str | None, has_archive: bool) -> Reference:
    if is_doi_url(url):
        return Reference("doi", doi_from_url(url), path, line_number, entry_key=entry_key, has_archive=has_archive)
    return Reference("url", url, path, line_number, entry_key=entry_key, has_archive=has_archive)


def reference_from_text_field(path: Path, line_number: int, line: str) -> Reference | None:
    match = TEXT_FIELD_RE.match(line)
    if not match:
        return None
    name = normalize_bib_field_name(match.group(1))
    value = clean_bib_value(match.group(2).strip().strip("`"))
    if name in DOI_FIELD_NAMES:
        return Reference("doi", normalize_doi(value), path, line_number)
    if name in ARCHIVE_URL_FIELD_NAMES:
        return Reference("archive_url", clean_url_token(value), path, line_number)
    if name in ACCESS_DATE_FIELD_NAMES:
        return Reference("access_date", value, path, line_number)
    return None


def extract_bibtex_references(path: Path) -> list[Reference]:
    text = read_text(path)
    references: list[Reference] = []
    for entry_key, entry_start, entry_text in iter_bib_entries(text):
        fields = bib_fields(entry_text, entry_start, text)
        has_archive = any(name in ARCHIVE_URL_FIELD_NAMES for name, _, _ in fields)
        for name, value, line_number in fields:
            if name in DOI_FIELD_NAMES:
                references.append(Reference("doi", normalize_doi(value), path, line_number, entry_key=entry_key))
            elif name in URL_FIELD_NAMES:
                references.append(reference_from_url(path, line_number, value, entry_key, has_archive))
            elif name in ARCHIVE_URL_FIELD_NAMES:
                references.append(Reference("archive_url", value, path, line_number, entry_key=entry_key))
            elif name in ACCESS_DATE_FIELD_NAMES:
                references.append(Reference("access_date", value, path, line_number, entry_key=entry_key))
    return references


def extract_text_references(path: Path) -> list[Reference]:
    references: list[Reference] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        field_reference = reference_from_text_field(path, line_number, line)
        if field_reference is not None:
            references.append(field_reference)
            if field_reference.kind in {"doi", "archive_url"}:
                continue
        for match in URL_TOKEN_RE.finditer(line):
            url = clean_url_token(match.group(0))
            references.append(reference_from_url(path, line_number, url, None, False))
    return mark_text_archive_coverage(dedupe_references(references))


def mark_text_archive_coverage(references: list[Reference]) -> list[Reference]:
    archived_targets = {
        original_url
        for reference in references
        if reference.kind == "archive_url"
        for original_url in [original_url_from_archive_url(reference.target)]
        if original_url
    }
    if not archived_targets:
        return references
    return [
        replace(reference, has_archive=True)
        if reference.kind == "url" and reference.target in archived_targets
        else reference
        for reference in references
    ]


def dedupe_references(references: list[Reference]) -> list[Reference]:
    seen: set[tuple[str, str, Path, int]] = set()
    unique_references: list[Reference] = []
    for reference in references:
        key = (reference.kind, reference.target, reference.path, reference.line_number)
        if key in seen:
            continue
        seen.add(key)
        unique_references.append(reference)
    return unique_references


def extract_references_from_file(path: Path) -> list[Reference]:
    if path.suffix.lower() == ".bib":
        return extract_bibtex_references(path)
    if path.suffix.lower() in DOCUMENT_SUFFIXES:
        return extract_text_references(path)
    return []


def iter_reference_files(paths: list[Path]) -> list[Path]:
    return iter_supported_files(paths, IGNORED_DIRS, SUPPORTED_SUFFIXES)


def request_status(
    url: str,
    client: UrlLibHttpClient,
    timeout: float,
    dns_attempts: int,
) -> HttpResponse:
    headers = {"User-Agent": USER_AGENT}
    attempts = max(dns_attempts, 1)
    last_dns_error: DnsCheckError | None = None
    for attempt_index in range(attempts):
        try:
            head_response = client.request("HEAD", url, timeout, headers)
            if head_response.status_code in GET_FALLBACK_STATUS_CODES:
                return client.request("GET", url, timeout, headers)
            return head_response
        except DnsCheckError as error:
            last_dns_error = error
            if attempt_index < attempts - 1:
                time.sleep(DNS_RETRY_DELAY_SECONDS)
    raise DnsCheckError(f"DNS lookup failed after {attempts} attempts") from last_dns_error


def category_for_status(status_code: int) -> str:
    if 200 <= status_code < 400:
        return "ok"
    if status_code in BROKEN_STATUS_CODES:
        return "broken"
    if status_code in WARNING_STATUS_CODES or status_code >= 500:
        return "warning"
    return "warning"


def message_for_status(status_code: int) -> str:
    if 200 <= status_code < 400:
        return f"HTTP {status_code}"
    if status_code in BROKEN_STATUS_CODES:
        return f"HTTP {status_code} likely broken"
    if status_code in WARNING_STATUS_CODES:
        return f"HTTP {status_code} may be access-controlled, rate-limited, or paywalled"
    if status_code >= 500:
        return f"HTTP {status_code} server error; result may be transient"
    return f"HTTP {status_code} uncertain"


def finding_for_http_error(reference: Reference, error: ReferenceCheckError, checked_url: str) -> Finding:
    if isinstance(error, DnsCheckError):
        return Finding("broken", reference, str(error), checked_url=checked_url)
    if isinstance(error, TimeoutCheckError):
        return Finding("warning", reference, f"Timeout: {error}", checked_url=checked_url)
    if isinstance(error, SslCheckError):
        return Finding("warning", reference, f"SSL error: {error}", checked_url=checked_url)
    return Finding("warning", reference, f"Network error: {error}", checked_url=checked_url)


def check_url(reference: Reference, client: UrlLibHttpClient, timeout: float, dns_attempts: int) -> Finding:
    if not is_valid_url(reference.target):
        return Finding("malformed_url", reference, "Malformed URL")
    try:
        response = request_status(reference.target, client, timeout, dns_attempts)
    except ReferenceCheckError as error:
        return finding_for_http_error(reference, error, reference.target)
    category = category_for_status(response.status_code)
    return Finding(
        category,
        reference,
        message_for_status(response.status_code),
        checked_url=response.url,
        status_code=response.status_code,
    )


def check_doi(reference: Reference, client: UrlLibHttpClient, timeout: float, dns_attempts: int) -> Finding:
    normalized_doi = normalize_doi(reference.target)
    doi_reference = Reference(
        reference.kind,
        normalized_doi,
        reference.path,
        reference.line_number,
        entry_key=reference.entry_key,
        has_archive=reference.has_archive,
    )
    if not is_valid_doi(normalized_doi):
        return Finding("malformed_doi", doi_reference, "Malformed DOI")
    checked_url = doi_resolver_url(normalized_doi)
    try:
        response = request_status(checked_url, client, timeout, dns_attempts)
    except ReferenceCheckError as error:
        return finding_for_http_error(doi_reference, error, checked_url)
    category = category_for_status(response.status_code)
    return Finding(
        category,
        doi_reference,
        f"DOI resolver returned {message_for_status(response.status_code)}",
        checked_url=response.url,
        status_code=response.status_code,
    )


def archive_availability_url(url: str) -> str:
    return f"https://archive.org/wayback/available?url={urllib.parse.quote(url, safe='')}"


def archive_save_url(url: str) -> str:
    return f"https://web.archive.org/save/{urllib.parse.quote(url, safe=':/?&=%#')}"


def archive_snapshot_available(response_body: str) -> bool:
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        return False
    closest = payload.get("archived_snapshots", {}).get("closest", {})
    return bool(closest.get("available"))


def check_archive_availability(
    reference: Reference,
    client: UrlLibHttpClient,
    timeout: float,
    allow_private_archive_submission: bool,
) -> Finding | None:
    if is_private_or_local_url(reference.target) and not allow_private_archive_submission:
        return Finding(
            "warning",
            reference,
            "Archive availability lookup skipped for private or local-looking URL",
        )
    availability_url = archive_availability_url(reference.target)
    headers = {"User-Agent": USER_AGENT}
    try:
        response = client.request("GET", availability_url, timeout, headers)
    except ReferenceCheckError as error:
        return finding_for_http_error(reference, error, availability_url)
    if category_for_status(response.status_code) != "ok":
        return Finding(
            "warning",
            reference,
            f"Archive availability endpoint returned {message_for_status(response.status_code)}",
            checked_url=response.url,
            status_code=response.status_code,
        )
    if archive_snapshot_available(response.body):
        return None
    return Finding("missing_archive", reference, "No Internet Archive snapshot reported", checked_url=response.url)


def create_archive_snapshot(
    reference: Reference,
    client: UrlLibHttpClient,
    timeout: float,
    allow_private_archive_submission: bool,
) -> Finding:
    if is_private_or_local_url(reference.target) and not allow_private_archive_submission:
        return Finding(
            "warning",
            reference,
            "Archive creation skipped for private or local-looking URL",
        )
    save_url = archive_save_url(reference.target)
    headers = {"User-Agent": USER_AGENT}
    try:
        response = client.request("GET", save_url, timeout, headers)
    except ReferenceCheckError as error:
        return finding_for_http_error(reference, error, save_url)
    return Finding(
        "warning",
        reference,
        f"Archive snapshot request submitted; verify manually. Endpoint returned HTTP {response.status_code}",
        checked_url=response.url,
        status_code=response.status_code,
    )


def should_check_archive(reference: Reference) -> bool:
    return (
        reference.kind == "url"
        and not reference.has_archive
        and is_valid_url(reference.target)
        and not is_archive_service_url(reference.target)
    )


def check_reference(
    reference: Reference,
    client: UrlLibHttpClient,
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    dns_attempts: int = DEFAULT_DNS_ATTEMPTS,
    check_archives: bool = False,
    create_archives: bool = False,
    allow_private_url_checks: bool = False,
    allow_private_archive_submission: bool = False,
) -> list[Finding]:
    if reference.kind == "access_date":
        return []
    if reference.kind == "doi":
        return [check_doi(reference, client, timeout, dns_attempts)]
    if not is_valid_url(reference.target):
        return [Finding("malformed_url", reference, "Malformed URL")]
    if is_private_or_local_url(reference.target) and not allow_private_url_checks:
        return [
            Finding(
                "warning",
                reference,
                "URL check skipped for private or local-looking URL",
            )
        ]

    primary_finding = check_url(reference, client, timeout, dns_attempts)
    findings = [primary_finding]
    if primary_finding.category != "ok" or not (check_archives or create_archives) or not should_check_archive(reference):
        return findings

    archive_finding = check_archive_availability(reference, client, timeout, allow_private_archive_submission)
    if archive_finding is None:
        return findings
    findings.append(archive_finding)
    if create_archives and archive_finding.category == "missing_archive":
        findings.append(create_archive_snapshot(reference, client, timeout, allow_private_archive_submission))
    return findings


def check_references(
    references: list[Reference],
    client: UrlLibHttpClient,
    *,
    timeout: float,
    dns_attempts: int,
    check_archives: bool,
    create_archives: bool,
    allow_private_url_checks: bool,
    allow_private_archive_submission: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    for reference in references:
        findings.extend(
            check_reference(
                reference,
                client,
                timeout=timeout,
                dns_attempts=dns_attempts,
                check_archives=check_archives,
                create_archives=create_archives,
                allow_private_url_checks=allow_private_url_checks,
                allow_private_archive_submission=allow_private_archive_submission,
            )
        )
    return findings


def count_by_category(findings: list[Finding]) -> dict[str, int]:
    counts = {category: 0 for category in CATEGORY_ORDER}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1
    return counts


def count_references_by_kind(references: list[Reference]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for reference in references:
        counts[reference.kind] = counts.get(reference.kind, 0) + 1
    return counts


def exit_code_for_findings(findings: list[Finding]) -> int:
    return 1 if any(finding.category in FAILING_CATEGORIES for finding in findings) else 0


def finding_to_dict(finding: Finding) -> dict[str, object]:
    return {
        "category": finding.category,
        "label": CATEGORY_LABELS.get(finding.category, finding.category),
        "message": finding.message,
        "status_code": finding.status_code,
        "checked_url": finding.checked_url,
        "reference": {
            "kind": finding.reference.kind,
            "target": finding.reference.target,
            "path": finding.reference.path.as_posix(),
            "line_number": finding.reference.line_number,
            "entry_key": finding.reference.entry_key,
            "has_archive": finding.reference.has_archive,
        },
    }


def report_payload(files: list[Path], references: list[Reference], findings: list[Finding]) -> dict[str, object]:
    return {
        "summary": {
            "scanned_files": len(files),
            "references": len(references),
            "checkable_references": len([reference for reference in references if reference.kind != "access_date"]),
            "reference_kinds": count_references_by_kind(references),
            "categories": count_by_category(findings),
            "exit_code": exit_code_for_findings(findings),
        },
        "findings": [finding_to_dict(finding) for finding in findings],
    }


def format_finding(finding: Finding) -> str:
    reference = finding.reference
    status = f" HTTP {finding.status_code}" if finding.status_code is not None else ""
    return (
        f"{reference.path}:{reference.line_number}: "
        f"{CATEGORY_LABELS.get(finding.category, finding.category)} "
        f"[{reference.kind}] {reference.target}{status} - {finding.message}"
    )


def printable_findings(findings: list[Finding], show_ok: bool) -> list[Finding]:
    if show_ok:
        return findings
    return [finding for finding in findings if finding.category != "ok"]


def print_summary(files: list[Path], references: list[Reference], findings: list[Finding], show_ok: bool) -> None:
    counts = count_by_category(findings)
    kind_counts = count_references_by_kind(references)
    print("External reference check")
    print(
        f"Scanned {len(files)} file(s), found {len(references)} reference field(s): "
        f"{kind_counts.get('url', 0)} URL(s), "
        f"{kind_counts.get('doi', 0)} DOI(s), "
        f"{kind_counts.get('archive_url', 0)} archive URL(s), "
        f"{kind_counts.get('access_date', 0)} access-date field(s)."
    )
    print(
        "Results: "
        + ", ".join(f"{CATEGORY_LABELS[category]}={counts.get(category, 0)}" for category in CATEGORY_ORDER)
    )
    details = printable_findings(findings, show_ok)
    if details:
        print("\nFindings:")
        for finding in details:
            print(f"- {format_finding(finding)}")
    else:
        print("\nNo broken or uncertain external references found.")
    if counts.get("warning", 0):
        print("\nWarnings are non-blocking because network checks can be transient or access-controlled.")
    if counts.get("missing_archive", 0):
        print("Missing archive findings are non-blocking; decide manually whether each URL should be archived.")


def markdown_report(files: list[Path], references: list[Reference], findings: list[Finding]) -> str:
    counts = count_by_category(findings)
    lines = [
        "# External Reference Check",
        "",
        f"- Scanned files: {len(files)}",
        f"- References: {len(references)}",
        f"- Exit code: {exit_code_for_findings(findings)}",
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- {CATEGORY_LABELS[category]}: {counts.get(category, 0)}" for category in CATEGORY_ORDER)
    lines.extend(["", "## Findings", ""])
    if findings:
        lines.extend(f"- {format_finding(finding)}" for finding in findings)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_reports(
    files: list[Path],
    references: list[Reference],
    findings: list[Finding],
    json_report: Path | None,
    markdown_report_path: Path | None,
) -> None:
    if json_report:
        write_text_file(json_report, json.dumps(report_payload(files, references, findings), indent=2) + "\n")
        print(f"Wrote JSON report: {json_report}")
    if markdown_report_path:
        write_text_file(markdown_report_path, markdown_report(files, references, findings))
        print(f"Wrote Markdown report: {markdown_report_path}")


def main(argv: list[str] | None = None) -> int:
    change_to_project_root()
    args = parse_args(argv)
    scan_paths = args.paths or DEFAULT_SCAN_ROOTS
    files = iter_reference_files(scan_paths)
    references = [reference for path in files for reference in extract_references_from_file(path)]
    client = UrlLibHttpClient()
    findings = check_references(
        references,
        client,
        timeout=args.timeout,
        dns_attempts=args.dns_attempts,
        check_archives=args.check_archives,
        create_archives=args.create_archives,
        allow_private_url_checks=args.allow_private_url_checks,
        allow_private_archive_submission=args.allow_private_archive_submission,
    )
    print_summary(files, references, findings, args.show_ok)
    write_reports(files, references, findings, args.json_report, args.markdown_report)
    return exit_code_for_findings(findings)


if __name__ == "__main__":
    sys.exit(main())
