"""
tests/test_groq_client.py
Unit tests for groq_client.py (mocked — no real API calls)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import MagicMock, patch
from groq_client import build_prompt, STYLE_INSTRUCTIONS


class TestBuildPrompt:
    def test_includes_title(self):
        prompt = build_prompt("Moby Dick", "Call me Ishmael...", "modern")
        assert "Moby Dick" in prompt

    def test_includes_style_instruction(self):
        prompt = build_prompt("Test", "Body text here.", "humorous")
        assert "humor" in prompt.lower() or "wit" in prompt.lower()

    def test_custom_style_included(self):
        prompt = build_prompt("Test", "Body.", "pirate")
        assert "pirate" in prompt.lower()

    def test_body_truncated_at_12000_chars(self):
        long_body = "x" * 20000
        prompt = build_prompt("Title", long_body, "modern")
        # The prompt should not contain more than 12000 'x' chars
        assert prompt.count("x") <= 12000


class TestStyleInstructions:
    def test_all_presets_exist(self):
        for style in ["original", "modern", "humorous", "professional", "academic", "casual"]:
            assert style in STYLE_INSTRUCTIONS
            assert len(STYLE_INSTRUCTIONS[style]) > 10


class TestSummarizeMocked:
    @patch("groq_client.Groq")
    def test_returns_content_string(self, mock_groq_class):
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "  This is a test digest.  "
        mock_client.chat.completions.create.return_value = mock_response

        from groq_client import summarize
        result = summarize("Title", "Body text.", "modern", "fake-key")

        assert result == "This is a test digest."
        mock_client.chat.completions.create.assert_called_once()
