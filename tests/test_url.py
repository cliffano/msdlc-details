"""Unit tests for msdlcdetails.url."""

import unittest

from msdlcdetails.errors import InvalidUrlError
from msdlcdetails.url import build_url, normalise_url, parse_url

CANONICAL = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"


class TestBuildUrl(unittest.TestCase):
    """Tests for build_url function."""

    def test_builds_canonical_url(self):
        """Test building canonical URLs from an ID and locale."""
        self.assertEqual(build_url(56519), CANONICAL)
        self.assertEqual(
            build_url(" 40784 ", "DE-DE"),
            "https://www.microsoft.com/de-de/download/details.aspx?id=40784",
        )

    def test_rejects_invalid_values(self):
        """Test that malformed IDs and locales raise an error."""
        cases = {
            "id": (("abc",), "Invalid download ID"),
            "negative id": (("-1",), "Invalid download ID"),
            "locale": ((1, "en_us/../x"), "Invalid locale"),
        }
        for name, (args, message) in cases.items():
            with self.subTest(name):
                with self.assertRaisesRegex(InvalidUrlError, message):
                    build_url(*args)


class TestParseUrl(unittest.TestCase):
    """Tests for parse_url function."""

    def test_parses_supported_forms(self):
        """Test extracting the ID and locale from supported URL forms."""
        cases = {
            CANONICAL: ("56519", "en-us"),
            "56519": ("56519", "en-us"),
            "https://www.microsoft.com/download/details.aspx?id=56519": (
                "56519",
                "en-us",
            ),
            "https://www.microsoft.com/ja-JP/download/details?id=102&ref=x": (
                "102",
                "ja-jp",
            ),
            "http://microsoft.com/en-us/download/details.aspx/?id=1": ("1", "en-us"),
        }
        for value, expected in cases.items():
            with self.subTest(value):
                self.assertEqual(parse_url(value), expected)
        self.assertEqual(parse_url(56519), ("56519", "en-us"))

    def test_rejects_invalid_urls(self):
        """Test that non-details URLs raise an error."""
        cases = {
            "ftp://www.microsoft.com/en-us/download/details.aspx?id=1": "Not a Microsoft",
            "https://evil.example/en-us/download/details.aspx?id=1": "Not a Microsoft",
            "https://www.microsoft.com.evil.example/download/details.aspx?id=1": (
                "Not a Microsoft"
            ),
            "https://www.microsoft.com/en-us/download/confirmation.aspx?id=1": (
                "Not a Download Center details"
            ),
            "https://www.microsoft.com/en-us/download/details.aspx": "Missing or invalid",
            "https://www.microsoft.com/en-us/download/details.aspx?id=x": (
                "Missing or invalid"
            ),
            "https://www.microsoft.com/en-us/download/details.aspx?id=1&id=2": (
                "Missing or invalid"
            ),
            "not a url": "Not a Microsoft",
        }
        for value, message in cases.items():
            with self.subTest(value):
                with self.assertRaisesRegex(InvalidUrlError, message):
                    parse_url(value)

    def test_invalid_url_error_is_value_error(self):
        """Test that InvalidUrlError can be caught as ValueError."""
        with self.assertRaises(ValueError):
            parse_url("nope")


class TestNormaliseUrl(unittest.TestCase):
    """Tests for normalise_url function."""

    def test_normalises_url_and_overrides_locale(self):
        """Test normalising a URL, with and without a locale override."""
        self.assertEqual(
            normalise_url("https://www.microsoft.com/download/details?id=56519"),
            CANONICAL,
        )
        self.assertEqual(
            normalise_url(CANONICAL, locale="fr-fr"),
            "https://www.microsoft.com/fr-fr/download/details.aspx?id=56519",
        )
