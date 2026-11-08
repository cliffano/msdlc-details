"""Unit tests for msdlcdetails.get_details."""

import unittest
from unittest.mock import MagicMock, patch

from msdlcdetails import InvalidUrlError, get_details
from tests.fixtures import SINGLE_FILE_VIEW, build_html

URL = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"


class TestGetDetails(unittest.TestCase):
    """Tests for get_details function."""

    @patch("msdlcdetails.fetch_html")
    @patch("msdlcdetails.init")
    def test_retrieves_details_by_id(self, mock_init, mock_fetch_html):
        """Test retrieving details by download ID."""
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger
        mock_fetch_html.return_value = build_html({"dlcDetailsView": SINGLE_FILE_VIEW})

        details = get_details(56519, timeout=10)

        mock_fetch_html.assert_called_once_with(URL, timeout=10)
        self.assertEqual(details.url, URL)
        self.assertTrue(
            details.download_url.endswith("ServiceTags_Public_20261102.json")
        )
        mock_logger.info.assert_any_call("Retrieving download details from %s", URL)
        mock_logger.info.assert_any_call("Found %s file(s) for download %s", 1, URL)

    @patch("msdlcdetails.fetch_html")
    @patch("msdlcdetails.init")
    def test_locale_override(self, _, mock_fetch_html):
        """Test that the locale argument overrides the URL locale."""
        mock_fetch_html.return_value = build_html({"dlcDetailsView": SINGLE_FILE_VIEW})
        get_details(URL, locale="ja-jp")
        self.assertEqual(
            mock_fetch_html.call_args[0][0],
            "https://www.microsoft.com/ja-jp/download/details.aspx?id=56519",
        )

    @patch("msdlcdetails.fetch_html")
    @patch("msdlcdetails.init")
    def test_invalid_url_is_not_fetched(self, _, mock_fetch_html):
        """Test that invalid URLs raise before any request is sent."""
        with self.assertRaises(InvalidUrlError):
            get_details("https://example.com/download/details.aspx?id=1")
        mock_fetch_html.assert_not_called()
