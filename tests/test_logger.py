"""Unit tests for msdlcdetails.logger."""

import logging
import unittest

from msdlcdetails import logger


class TestLogger(unittest.TestCase):
    """Tests for init function."""

    def test_init_creates_and_caches_logger(self):
        """Test that init creates a logger once and then reuses it."""
        logger.LOGGER = None
        first = logger.init()
        self.assertIsInstance(first, logging.LoggerAdapter)
        self.assertIs(logger.init(), first)
