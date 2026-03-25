"""
tests/test_content_filter.py
Unit tests for content_filter.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from content_filter import is_clean, sanitize, check_and_clean


class TestIsClean:
    def test_clean_text_passes(self):
        assert is_clean("The quick brown fox jumps over the lazy dog.") is True

    def test_empty_string_passes(self):
        assert is_clean("") is True


class TestSanitize:
    def test_clean_text_unchanged(self):
        text = "Hello, world! This is a professional summary."
        assert sanitize(text) == text


class TestCheckAndClean:
    def test_clean_returns_true_and_original(self):
        text = "This is a perfectly fine summary of the document."
        is_safe, result = check_and_clean(text)
        assert is_safe is True
        assert result == text
