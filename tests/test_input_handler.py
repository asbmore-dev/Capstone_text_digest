"""
tests/test_input_handler.py
Unit tests for the input handler module.
"""

import io
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from input_handler import detect_title, _split_title_body, extract_from_txt


class TestDetectTitle:
    def test_returns_first_nonempty_line(self):
        text = "\n\nMoby Dick\nCall me Ishmael..."
        assert detect_title(text) == "Moby Dick"

    def test_caps_at_120_chars(self):
        long_line = "A" * 200
        result = detect_title(long_line)
        assert len(result) == 120

    def test_empty_text_returns_untitled(self):
        assert detect_title("   \n  \n") == "Untitled"


class TestSplitTitleBody:
    def test_splits_correctly(self):
        text = "My Title\n\nParagraph one.\nParagraph two."
        title, body = _split_title_body(text)
        assert title == "My Title"
        assert "Paragraph one" in body

    def test_single_line(self):
        title, body = _split_title_body("Only a title")
        assert title == "Only a title"
        assert body == ""


class TestExtractFromTxt:
    def test_basic_extraction(self):
        content = b"The Great Gatsby\n\nIn my younger and more vulnerable years..."
        title, body = extract_from_txt(content)
        assert title == "The Great Gatsby"
        assert "younger" in body

    def test_handles_utf8(self):
        content = "Café au lait\nBonjour monde".encode("utf-8")
        title, body = extract_from_txt(content)
        assert "Café" in title
