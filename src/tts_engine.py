"""
tts_engine.py
Text-to-speech engine using Google Text-to-Speech (gTTS).

Public API:
    get_audio_bytes(text, lang='en') -> bytes
"""

from __future__ import annotations

import io


# ── Core TTS function ─────────────────────────────────────────────────────────

def text_to_speech(text: str, lang: str = "en") -> io.BytesIO:
    """
    Convert text to an MP3 audio stream using gTTS.

    Args:
        text: The text to convert to speech.
        lang: BCP-47 language code. Default 'en' (English).

    Returns:
        BytesIO buffer containing MP3 audio data.

    Raises:
        ImportError:  If gTTS is not installed.
        RuntimeError: If the gTTS request fails (e.g. no internet).
    """
    try:
        from gtts import gTTS
    except ImportError:
        raise ImportError("Install gTTS: uv add gtts")

    # gTTS has a practical limit — very long texts can time out.
    # Truncate to ~3,000 words to stay within safe limits.
    words = text.split()
    if len(words) > 3000:
        text = " ".join(words[:3000]) + " … audio truncated at 3000 words."

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
    except Exception as exc:
        raise RuntimeError(
            f"gTTS failed to generate audio: {exc}. "
            "Check your internet connection — gTTS requires network access."
        ) from exc

    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer


# ── Streamlit wrapper ─────────────────────────────────────────────────────────

def get_audio_bytes(text: str, lang: str = "en") -> bytes:
    """
    Convert text to MP3 and return raw bytes for Streamlit's st.audio().

    Args:
        text: The full digest text (including headers).
        lang: BCP-47 language code. Default 'en'.

    Returns:
        MP3 audio as a bytes object.
    """
    buffer = text_to_speech(text, lang=lang)
    return buffer.read()
