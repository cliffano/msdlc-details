"""Unit tests for msdlcdetails.fetcher."""

import unittest
from email.message import Message
from http.client import IncompleteRead
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from msdlcdetails.errors import FetchError
from msdlcdetails.fetcher import DEFAULT_HEADERS, fetch_html

URL = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"


def _response(body: bytes, content_type: str) -> MagicMock:
    """Build a mock urlopen response.

    :param body: Response body.
    :param content_type: Value of the Content-Type header.
    :returns: Mock usable as a context manager.
    """
    headers = Message()
    headers["Content-Type"] = content_type
    response = MagicMock()
    response.headers = headers
    response.read.return_value = body
    response.__enter__.return_value = response
    return response


class TestFetchHtml(unittest.TestCase):
    """Tests for fetch_html function."""

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_returns_decoded_body_with_browser_headers(self, mock_urlopen, _):
        """Test decoding with the response charset and sending headers."""
        mock_urlopen.return_value = _response(
            "Café".encode("latin-1"), "text/html; charset=iso-8859-1"
        )

        html = fetch_html(URL, timeout=5, headers={"Accept-Language": "de-DE"})

        self.assertEqual(html, "Café")
        request = mock_urlopen.call_args[0][0]
        self.assertEqual(request.full_url, URL)
        self.assertEqual(
            request.get_header("User-agent"), DEFAULT_HEADERS["User-Agent"]
        )
        self.assertEqual(request.get_header("Accept-language"), "de-DE")
        self.assertEqual(mock_urlopen.call_args.kwargs, {"timeout": 5})

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_defaults_to_utf8(self, mock_urlopen, _):
        """Test that bodies without a charset are decoded as UTF-8."""
        mock_urlopen.return_value = _response("Café".encode("utf-8"), "text/html")
        self.assertEqual(fetch_html(URL), "Café")

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_http_error(self, mock_urlopen, _):
        """Test that HTTP errors raise FetchError with the status."""
        mock_urlopen.side_effect = HTTPError(URL, 403, "Forbidden", Message(), None)
        with self.assertRaisesRegex(FetchError, "HTTP 403") as context:
            fetch_html(URL)
        self.assertEqual(context.exception.status, 403)
        self.assertEqual(context.exception.url, URL)

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_http_error_is_not_retried(self, mock_urlopen, _):
        """Test that HTTP error statuses are not retried."""
        mock_urlopen.side_effect = HTTPError(URL, 500, "Error", Message(), None)
        with self.assertRaisesRegex(FetchError, "HTTP 500"):
            fetch_html(URL, retries=3)
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_transient_errors_exhaust_retries(self, mock_urlopen, mock_init):
        """Test that transient errors are retried, then raise FetchError."""
        errors = (
            URLError("refused"),
            TimeoutError("timed out"),
            IncompleteRead(b"partial", 10),
        )
        for error in errors:
            with self.subTest(type(error).__name__):
                mock_urlopen.reset_mock()
                mock_urlopen.side_effect = error
                with self.assertRaisesRegex(FetchError, "after 3 attempt") as context:
                    fetch_html(URL)
                self.assertIsNone(context.exception.status)
                self.assertEqual(mock_urlopen.call_count, 3)
        self.assertEqual(mock_init.return_value.warning.call_count, 6)

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_transient_error_recovers_on_retry(self, mock_urlopen, _):
        """Test that a retry after a truncated response succeeds."""
        mock_urlopen.side_effect = [
            IncompleteRead(b"partial", 10),
            _response(b"<html></html>", "text/html"),
        ]
        self.assertEqual(fetch_html(URL), "<html></html>")
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("msdlcdetails.fetcher.init")
    @patch("msdlcdetails.fetcher.urlopen")
    def test_negative_retries_makes_single_attempt(self, mock_urlopen, _):
        """Test that negative retries are treated as zero."""
        mock_urlopen.side_effect = URLError("refused")
        with self.assertRaisesRegex(FetchError, "after 1 attempt"):
            fetch_html(URL, retries=-1)
        self.assertEqual(mock_urlopen.call_count, 1)
