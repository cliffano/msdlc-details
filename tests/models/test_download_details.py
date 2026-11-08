"""Unit tests for msdlcdetails.models.download_details."""

import unittest

from msdlcdetails.models import DownloadDetails, DownloadFile

ARM = DownloadFile(name="vcredist_arm.exe", url="https://d/arm")
X86 = DownloadFile(name="vcredist_x86.exe", url="https://d/x86")
X64 = DownloadFile(name="VCRedist_x64.exe", url="https://d/x64", is_primary=True)


def _details(files: list[DownloadFile]) -> DownloadDetails:
    """Build download details offering the given files.

    :param files: Files offered by the download.
    :returns: Download details.
    """
    return DownloadDetails(
        details_id="1", url="", locale="en-us", title="T", files=files
    )


class TestDownloadDetails(unittest.TestCase):
    """Tests for DownloadDetails class."""

    def test_primary_file_prefers_flagged_file(self):
        """Test that the file flagged as primary is preferred."""
        details = _details([ARM, X64, X86])
        self.assertEqual(details.primary_file, X64)
        self.assertEqual(details.download_url, "https://d/x64")

    def test_primary_file_falls_back_to_first_file(self):
        """Test that the first file is used when none is flagged."""
        details = _details([ARM, X86])
        self.assertEqual(details.primary_file, ARM)
        self.assertEqual(details.download_url, "https://d/arm")

    def test_no_files(self):
        """Test that a download without files has no primary file."""
        details = _details([])
        self.assertIsNone(details.primary_file)
        self.assertIsNone(details.download_url)

    def test_find_file(self):
        """Test case-insensitive shell-style file name matching."""
        details = _details([ARM, X86, X64])
        cases = {
            "*x64*.exe": X64,
            "VCREDIST_X86.EXE": X86,
            "vcredist_*": ARM,
            "*.msi": None,
        }
        for pattern, expected in cases.items():
            with self.subTest(pattern):
                self.assertEqual(details.find_file(pattern), expected)

    def test_raw_excluded_from_equality_and_repr(self):
        """Test that raw page data does not affect equality or repr."""
        first = DownloadDetails("1", "", "en-us", "T", raw={"a": 1})
        second = DownloadDetails("1", "", "en-us", "T", raw={"b": 2})
        self.assertEqual(first, second)
        self.assertNotIn("raw", repr(first))
