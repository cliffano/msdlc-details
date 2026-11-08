"""Integration tests for get_details against the live Download Center."""

import unittest

from msdlcdetails import DetailsNotFoundError, FetchError, get_details

URL = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"


class TestGetDetails(unittest.TestCase):
    """Integration tests for get_details function."""

    def test_azure_service_tags(self):
        """Test retrieving the current Azure Service Tags file URL."""
        details = get_details(URL)

        self.assertEqual(details.details_id, "56519")
        self.assertIn("Service Tags", details.title)
        self.assertIsNotNone(details.primary_file)
        self.assertRegex(
            details.download_url,
            r"^https://download\.microsoft\.com/download/.+/"
            r"ServiceTags_Public_\d{8}\.json$",
        )
        self.assertGreater(details.primary_file.size, 0)
        self.assertIsNotNone(details.primary_file.date_published)

    def test_multi_file_download(self):
        """Test selecting one file from a multi-file download."""
        details = get_details(40784)

        self.assertGreater(len(details.files), 1)
        self.assertIsNotNone(details.find_file("*x64*.exe"))

    def test_unknown_download(self):
        """Test that an unknown download ID raises an error."""
        with self.assertRaises((DetailsNotFoundError, FetchError)):
            get_details(1, timeout=20)
