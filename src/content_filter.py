"""
content_filter.py
Profanity and content safety check for digest output.

Public API:
    check_and_clean(text) -> (is_safe: bool, cleaned_text: str)
"""

from __future__ import annotations


# ── Core check functions ──────────────────────────────────────────────────────

def is_clean(text: str) -> bool:
    """
    Return True if the text contains no flagged words.
    Uses better-profanity's default word list.
    """
    try:
        from better_profanity import profanity
    except ImportError:
        raise ImportError("Install better-profanity: uv add better-profanity")

    profanity.load_censor_words()
    return not profanity.contains_profanity(text)


def sanitize(text: str) -> str:
    """
    Replace flagged words with *** and return the cleaned string.
    """
    try:
        from better_profanity import profanity
    except ImportError:
        raise ImportError("Install better-profanity: uv add better-profanity")

    profanity.load_censor_words()
    return profanity.censor(text, censor_char="*")


# ── Public entry point ────────────────────────────────────────────────────────

def check_and_clean(text: str) -> tuple[bool, str]:
    """
    Check the text for inappropriate content and return a cleaned version.

    Args:
        text: The raw digest string from groq_client.

    Returns:
        (is_safe, cleaned_text)
        - is_safe:      True if no flagged content was found.
        - cleaned_text: Original text if safe, censored text if flagged.
    """
    try:
        clean = is_clean(text)
    except Exception:
        # If the filter itself fails for any reason, pass the text through
        # rather than blocking the user — fail open, not closed.
        return True, text

    if clean:
        return True, text

    # Sanitize and return flagged status
    cleaned = sanitize(text)
    return False, cleaned
