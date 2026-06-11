from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_external_references


class FakeHttpClient:
    def __init__(
        self,
        responses: dict[
            tuple[str, str],
            check_external_references.HttpResponse | check_external_references.ReferenceCheckError,
        ],
    ) -> None:
        self.responses = responses
        self.requests: list[tuple[str, str]] = []

    def request(
        self,
        method: str,
        url: str,
        timeout: float,
        headers: dict[str, str],
    ) -> check_external_references.HttpResponse:
        self.requests.append((method, url))
        response = self.responses[(method, url)]
        if isinstance(response, Exception):
            raise response
        return response


def reference(target: str, kind: str = "url") -> check_external_references.Reference:
    return check_external_references.Reference(
        kind=kind,
        target=target,
        path=Path("manuscript/chapter.qmd"),
        line_number=7,
    )


class CheckExternalReferencesTests(unittest.TestCase):
    def test_valid_url_is_ok(self) -> None:
        url = "https://example.com/source"
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.HttpResponse(200, url),
        })

        findings = check_external_references.check_reference(reference(url), client)

        self.assertEqual([finding.category for finding in findings], ["ok"])

    def test_404_is_broken(self) -> None:
        url = "https://example.com/missing"
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.HttpResponse(404, url),
        })

        findings = check_external_references.check_reference(reference(url), client)

        self.assertEqual(findings[0].category, "broken")

    def test_403_is_warning_after_get_fallback(self) -> None:
        url = "https://example.com/paywalled"
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.HttpResponse(403, url),
            ("GET", url): check_external_references.HttpResponse(403, url),
        })

        findings = check_external_references.check_reference(reference(url), client)

        self.assertEqual(findings[0].category, "warning")
        self.assertEqual(client.requests, [("HEAD", url), ("GET", url)])

    def test_timeout_is_warning(self) -> None:
        url = "https://example.com/slow"
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.TimeoutCheckError("timed out"),
        })

        findings = check_external_references.check_reference(reference(url), client)

        self.assertEqual(findings[0].category, "warning")

    def test_malformed_url_is_reported_without_network_request(self) -> None:
        malformed_urls = [
            "https:// bad.example/source",
            "https://example.com:bad/source",
        ]
        for malformed_url in malformed_urls:
            with self.subTest(url=malformed_url):
                client = FakeHttpClient({})

                findings = check_external_references.check_reference(reference(malformed_url), client)

                self.assertEqual(findings[0].category, "malformed_url")
                self.assertEqual(client.requests, [])

    def test_private_or_local_urls_are_skipped_without_network_request_by_default(self) -> None:
        private_urls = [
            "http://localhost:11434/status",
            "http://127.0.0.1/admin",
            "http://10.0.0.5/source",
            "http://169.254.169.254/latest/meta-data",
            "http://drafts.local/source",
            "http://intranet/source",
        ]
        for private_url in private_urls:
            with self.subTest(url=private_url):
                client = FakeHttpClient({
                    ("HEAD", private_url): check_external_references.HttpResponse(200, private_url),
                })

                findings = check_external_references.check_reference(reference(private_url), client)

                self.assertEqual(findings[0].category, "warning")
                self.assertIn("skipped", findings[0].message)
                self.assertEqual(client.requests, [])

    def test_private_url_check_can_be_explicitly_enabled(self) -> None:
        url = "http://127.0.0.1/status"
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.HttpResponse(200, url),
        })

        findings = check_external_references.check_reference(
            reference(url),
            client,
            allow_private_url_checks=True,
        )

        self.assertEqual([finding.category for finding in findings], ["ok"])
        self.assertEqual(client.requests, [("HEAD", url)])

    def test_malformed_doi_is_reported_without_network_request(self) -> None:
        client = FakeHttpClient({})

        findings = check_external_references.check_reference(reference("not a doi", "doi"), client)

        self.assertEqual(findings[0].category, "malformed_doi")
        self.assertEqual(client.requests, [])

    def test_doi_resolution_success_and_failure(self) -> None:
        doi = "10.1234/example.doi"
        doi_url = f"https://doi.org/{doi}"
        success_client = FakeHttpClient({
            ("HEAD", doi_url): check_external_references.HttpResponse(302, doi_url),
        })
        failure_client = FakeHttpClient({
            ("HEAD", doi_url): check_external_references.HttpResponse(404, doi_url),
        })

        success = check_external_references.check_reference(reference(doi, "doi"), success_client)
        failure = check_external_references.check_reference(reference(doi, "doi"), failure_client)

        self.assertEqual(success[0].category, "ok")
        self.assertEqual(failure[0].category, "broken")

    def test_archive_detection_does_not_create_archive_snapshots(self) -> None:
        url = "https://example.com/source"
        availability_url = check_external_references.archive_availability_url(url)
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.HttpResponse(200, url),
            ("GET", availability_url): check_external_references.HttpResponse(
                200,
                availability_url,
                json.dumps({"archived_snapshots": {"closest": {"available": True}}}),
            ),
        })

        findings = check_external_references.check_reference(reference(url), client, check_archives=True)

        self.assertEqual([finding.category for finding in findings], ["ok"])
        self.assertFalse(any("web.archive.org/save/" in url for _, url in client.requests))

    def test_missing_archive_is_reported_without_failing_primary_url(self) -> None:
        url = "https://example.com/source"
        availability_url = check_external_references.archive_availability_url(url)
        client = FakeHttpClient({
            ("HEAD", url): check_external_references.HttpResponse(200, url),
            ("GET", availability_url): check_external_references.HttpResponse(
                200,
                availability_url,
                json.dumps({"archived_snapshots": {}}),
            ),
        })

        findings = check_external_references.check_reference(reference(url), client, check_archives=True)

        self.assertEqual([finding.category for finding in findings], ["ok", "missing_archive"])
        self.assertEqual(check_external_references.exit_code_for_findings(findings), 0)

    def test_bibtex_extraction_finds_url_doi_archive_and_access_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "references.bib"
            path.write_text(
                "\n".join(
                    [
                        "@article{smith2026,",
                        "  title = {Example},",
                        "  doi = {10.1234/example.doi},",
                        "  url = {https://example.com/article},",
                        "  archive_url = {https://web.archive.org/web/20260101000000/https://example.com/article},",
                        "  urldate = {2026-01-01},",
                        "}",
                    ]
                ),
                encoding="utf-8",
            )

            references = check_external_references.extract_references_from_file(path)

        self.assertEqual(
            [(item.kind, item.target, item.line_number) for item in references],
            [
                ("doi", "10.1234/example.doi", 3),
                ("url", "https://example.com/article", 4),
                (
                    "archive_url",
                    "https://web.archive.org/web/20260101000000/https://example.com/article",
                    5,
                ),
                ("access_date", "2026-01-01", 6),
            ],
        )

    def test_markdown_extraction_treats_doi_org_links_as_doi_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "chapter.qmd"
            path.write_text(
                "See https://doi.org/10.1234/example.doi and https://example.com/source.\n",
                encoding="utf-8",
            )

            references = check_external_references.extract_references_from_file(path)

        self.assertEqual(
            [(item.kind, item.target) for item in references],
            [
                ("doi", "10.1234/example.doi"),
                ("url", "https://example.com/source"),
            ],
        )

    def test_markdown_extraction_finds_metadata_style_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "source-note.md"
            path.write_text(
                "\n".join(
                    [
                        "doi: 10.1234/example.doi",
                        "archive_url: https://web.archive.org/web/20260101000000/https://example.com/article",
                        "urldate: 2026-01-01",
                    ]
                ),
                encoding="utf-8",
            )

            references = check_external_references.extract_references_from_file(path)

        self.assertEqual(
            [(item.kind, item.target, item.line_number) for item in references],
            [
                ("doi", "10.1234/example.doi", 1),
                (
                    "archive_url",
                    "https://web.archive.org/web/20260101000000/https://example.com/article",
                    2,
                ),
                ("access_date", "2026-01-01", 3),
            ],
        )

    def test_markdown_url_is_marked_archived_when_archive_url_points_to_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "source-note.md"
            path.write_text(
                "\n".join(
                    [
                        "url: https://example.com/article",
                        "archive_url: https://web.archive.org/web/20260101000000/https://example.com/article",
                    ]
                ),
                encoding="utf-8",
            )

            references = check_external_references.extract_references_from_file(path)

        url_reference = next(item for item in references if item.kind == "url")
        self.assertTrue(url_reference.has_archive)


if __name__ == "__main__":
    unittest.main()
