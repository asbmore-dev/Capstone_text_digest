"""
groq_client.py
Groq API wrapper for Capstone_text_digest.

Public API:
    summarize(title, body, style, api_key, reduction_pct) -> str
"""

from __future__ import annotations

# ── Constants ─────────────────────────────────────────────────────────────────

MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 2048

# Style guidance injected into the system prompt
_STYLE_HINTS: dict[str, str] = {
    "original":     "Preserve the author's original tone and vocabulary as closely as possible.",
    "modern":       "Use clear, contemporary language. Short sentences, active voice.",
    "humorous":     "Add light wit and playful asides while keeping the core meaning intact.",
    "professional": "Use formal, precise language suitable for a business or executive audience.",
    "academic":     "Use scholarly language with clear argumentation and neutral tone.",
    "casual":       "Write in a friendly, conversational tone as if explaining to a friend.",
}


# ── Prompt builders ───────────────────────────────────────────────────────────

def build_prompt(title: str, body: str, style: str, reduction_pct: int | None) -> str:
    """
    Build the user message sent to Groq.
    If reduction_pct is None, Groq chooses the best length automatically.
    """
    style_hint = _STYLE_HINTS.get(style.lower(), f'Write in a "{style}" style.')

    if reduction_pct is not None:
        target_pct = 100 - reduction_pct
        length_instruction = (
            f"Target length: approximately {target_pct}% of the original length "
            f"({reduction_pct}% reduction)."
        )
    else:
        length_instruction = (
            "Target length: use your best judgement to produce a concise, "
            "well-rounded summary — typically 20–40% of the original length."
        )

    return (
        f'Title: {title}\n\n'
        f'{body}\n\n'
        f'---\n'
        f'Summarise the text above.\n'
        f'{length_instruction}\n'
        f'Style instruction: {style_hint}\n'
        f'Return only the summary text — no preamble, no "Here is a summary:", '
        f'no closing remarks.'
    )


def _system_prompt() -> str:
    return (
        "You are an expert editor and summariser. "
        "When given a text, you produce a faithful, well-structured digest "
        "that respects the requested style and length target. "
        "Never add introductory phrases like 'Here is a summary' or 'In conclusion'. "
        "Output only the digest text itself."
    )


# ── Main public function ──────────────────────────────────────────────────────

def summarize(
    title: str,
    body: str,
    style: str,
    api_key: str,
    reduction_pct: int | None = None,
) -> str:
    """
    Send title + body to Groq and return the digest string.

    Args:
        title:         Document title.
        body:          Full source text.
        style:         Style preset or custom style string.
        api_key:       Groq API key.
        reduction_pct: How much to reduce the text (10–90). Default 50.

    Returns:
        The digest as a plain string.

    Raises:
        RuntimeError: On API or network errors.
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install groq: uv add groq")

    client = Groq(api_key=api_key)

    messages = [
        {"role": "system", "content": _system_prompt()},
        {"role": "user",   "content": build_prompt(title, body, style, reduction_pct)},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=0.7,
            messages=messages,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API request failed: {exc}") from exc

    digest = response.choices[0].message.content.strip()

    if not digest:
        raise RuntimeError("Groq returned an empty response. Please try again.")

    return digest


# ── Safe retry (used by content_filter if a re-prompt is needed) ──────────────

def _safe_retry(title: str, body: str, style: str, api_key: str, reduction_pct: int = 50) -> str:
    """
    Re-request the digest with an explicit instruction to avoid any
    inappropriate language. Called by content_filter when the first
    pass fails the safety check.
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install groq: uv add groq")

    client = Groq(api_key=api_key)

    clean_instruction = (
        "IMPORTANT: Your response must be completely free of profanity, "
        "hate speech, or any inappropriate language."
    )

    messages = [
        {"role": "system", "content": _system_prompt() + "\n\n" + clean_instruction},
        {"role": "user",   "content": build_prompt(title, body, style, reduction_pct)},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=0.5,   # lower temperature for safer output
            messages=messages,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq safe-retry failed: {exc}") from exc

    return response.choices[0].message.content.strip()
