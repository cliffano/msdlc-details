"""Unit tests for msdlcdetails.parser."""

import unittest
from datetime import datetime

from msdlcdetails.errors import DetailsNotFoundError
from msdlcdetails.models import Locale, RelatedResource
from msdlcdetails.parser import extract_state, parse_details
from tests.fixtures import MULTI_FILE_VIEW, SINGLE_FILE_VIEW, build_html


class TestExtractState(unittest.TestCase):
    """Tests for extract_state function."""

    def test_extracts_details_view(self):
        """Test that the embedded details view is returned."""
        view = extract_state(build_html({"dlcDetailsView": SINGLE_FILE_VIEW}))
        self.assertEqual(view, SINGLE_FILE_VIEW)

    def test_ignores_trailing_script_content(self):
        """Test that script content after the JSON object is ignored."""
        html = build_html({"dlcDetailsView": SINGLE_FILE_VIEW}).replace(
            "</script>", ";window.other={};</script>", 1
        )
        self.assertEqual(extract_state(html)["detailsId"], "56519")

    def test_invalid_pages_raise_details_not_found(self):
        """Test that pages without valid details data raise an error."""
        cases = {
            "no marker": ("<html></html>", "does not contain"),
            "no assignment": ("<script>window.__DLCDetails__</script>", "Malformed"),
            "bad json": ("<script>window.__DLCDetails__={oops</script>", "decode"),
            "not object": (build_html([1, 2]), "no details view"),
            "no view": (build_html({"other": {}}), "no details view"),
            "view not dict": (build_html({"dlcDetailsView": "x"}), "no details view"),
            "error": (
                build_html({"dlcDetailsView": {"error": "Not found"}}),
                "Download Center error: Not found",
            ),
        }
        for name, (html, message) in cases.items():
            with self.subTest(name):
                with self.assertRaisesRegex(DetailsNotFoundError, message):
                    extract_state(html)


class TestParseDetails(unittest.TestCase):
    """Tests for parse_details function."""

    def test_single_file_page(self):
        """Test parsing every field of a single-file download page."""
        url = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"
        details = parse_details(
            build_html({"dlcDetailsView": SINGLE_FILE_VIEW}), url=url
        )

        self.assertEqual(details.details_id, "56519")
        self.assertEqual(details.url, url)
        self.assertEqual(details.locale, "en-us")
        self.assertEqual(
            details.title, "Azure IP Ranges and Service Tags – Public Cloud"
        )
        self.assertEqual(details.version, "2026.11.02")
        self.assertEqual(details.date_published, "11/3/2026")
        self.assertEqual(details.system_requirements, "Json reader recommended")
        self.assertEqual(details.supported_os, ["Windows Server 2016"])
        self.assertEqual(
            details.install_instructions, "Download the new json file every week."
        )
        self.assertEqual(details.additional_information, "")
        self.assertEqual(details.related_resources, [])
        self.assertEqual(details.available_locales, [Locale("en-us", "English")])
        self.assertEqual(details.raw, SINGLE_FILE_VIEW)

        self.assertEqual(len(details.files), 1)
        download_file = details.files[0]
        self.assertEqual(download_file.name, "ServiceTags_Public_20261102.json")
        self.assertTrue(download_file.url.endswith("ServiceTags_Public_20261102.json"))
        self.assertEqual(download_file.size, 4570790)
        self.assertEqual(download_file.version, "2026.11.02")
        self.assertEqual(
            download_file.date_published, datetime(2026, 11, 3, 13, 53, 19)
        )
        self.assertEqual(download_file.date_published_raw, "11/3/2026 1:53:19 PM")
        self.assertFalse(download_file.is_primary)
        self.assertEqual(details.download_url, download_file.url)

    def test_multi_file_page(self):
        """Test parsing a multi-file page with a primary file."""
        details = parse_details(build_html({"dlcDetailsView": MULTI_FILE_VIEW}))

        self.assertEqual(details.details_id, "102")
        self.assertEqual(details.url, "")
        self.assertEqual(details.description, "")
        self.assertEqual(details.supported_os, [])
        self.assertEqual(
            details.related_resources,
            [RelatedResource("Developer Center", "http://go.microsoft.com/fwlink/")],
        )
        self.assertEqual(
            [locale.culture_code for locale in details.available_locales],
            ["en-us", "ja-jp"],
        )
        self.assertIn("Readme", details.additional_information)

        unparseable = details.files[1]
        self.assertTrue(unparseable.is_primary)
        self.assertIsNone(unparseable.size)
        self.assertIsNone(unparseable.date_published)
        self.assertEqual(unparseable.date_published_raw, "15.07.2024 03:08:07")
        self.assertEqual(details.primary_file, unparseable)

    def test_minimal_page(self):
        """Test that missing fields fall back to empty values."""
        details = parse_details(
            build_html(
                {"dlcDetailsView": {"downloadFile": [{}], "localeDropdown": None}}
            )
        )
        self.assertEqual(details.details_id, "")
        self.assertEqual(details.title, "")
        self.assertEqual(details.available_locales, [])
        download_file = details.files[0]
        self.assertEqual(download_file.name, "")
        self.assertIsNone(download_file.size)
        self.assertIsNone(download_file.date_published)
        self.assertFalse(download_file.is_primary)

    def test_page_without_files(self):
        """Test a page that offers no files."""
        details = parse_details(build_html({"dlcDetailsView": {"downloadFile": None}}))
        self.assertEqual(details.files, [])
        self.assertIsNone(details.download_url)
