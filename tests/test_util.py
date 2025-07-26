"""
Tests for utility functions.
Equivalent to UtilTest.java
"""

import unittest

from pyjavapoet.util import is_ascii_upper


class UtilTest(unittest.TestCase):
    """Test utility functions."""

    def test_is_ascii_upper(self):
        """Test is_ascii_upper function."""
        self.assertTrue(is_ascii_upper("ABC"))
        self.assertFalse(is_ascii_upper("abc"))
        self.assertFalse(is_ascii_upper("123"))
        self.assertFalse(is_ascii_upper(""))
        self.assertFalse(is_ascii_upper(" "))


if __name__ == "__main__":
    unittest.main()
