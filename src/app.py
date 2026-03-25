"""
Capstone_text_digest — app.py
Streamlit entry point
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Helper ────────────────────────────────────────────────────────────────────
def _mime_for(fmt: str) -> str:
    return {
        "txt":  "text/plain",
        "pdf":  "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "rtf":  "application/rtf",
        "html": "text/html",
    }.get(fmt, "application/octet-stream")


def _word_count(text: str) -> int:
    return len(text.split())


def _char_count(text: str) -> int:
    return len(text)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Capstone Text Digest",
    page_icon="📄",
    layout="wide",
)

# ── CSS: move sidebar to the right ───────────────────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            order: 1;
        }
        [data-testid="stSidebarContent"] {
            order: 1;
        }
        .main .block-container {
            order: 0;
        }
        section[data-testid="stSidebar"] {
            left: auto;
            right: 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Capstone Text Digest")
st.caption("Transform any text into a polished, styled summary using Groq AI.")

# ── Right Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")

    api_key = os.getenv("GROQ_API_KEY", "")

    PRESET_STYLES = ["original", "modern", "humorous", "professional", "academic", "casual"]
    style_preset = st.selectbox("Output Style (preset)", PRESET_STYLES)
    custom_style = st.text_input("Or type a custom style", placeholder="e.g. pirate, Hemingway, Gen-Z")
    chosen_style = custom_style.strip() if custom_style.strip() else style_preset

    st.divider()

    # ── Reduction mode toggle ─────────────────────────────────────────────────
    use_target_reduction = st.toggle(
        "Set target output reduction",
        value=False,
        help="On: set a specific reduction % with the slider. "
             "Off: let Groq decide the best length automatically.",
    )

    if use_target_reduction:
        reduction_pct = st.slider(
            "Target reduction",
            min_value=10,
            max_value=90,
            value=50,
            step=5,
            format="%d%%",
            help="How much shorter the digest should be vs. the original.",
        )
    else:
        reduction_pct = None   # signals groq_client to use default behaviour

    st.divider()

    output_format = st.selectbox(
        "Output Format",
        ["txt", "pdf", "docx", "rtf", "html"],
    )

    voice_reading = st.toggle("Enable Voice Reading", value=False)

    st.divider()
    st.markdown("**Model:** `llama-3.1-8b-instant` (free)")
    st.markdown("**TTS:** Google Text-to-Speech (free)")

    # ── Statistics panel ──────────────────────────────────────────────────────
    st.divider()
    st.header("Statistics")

    if "stats" in st.session_state and st.session_state.stats:
        s = st.session_state.stats
        st.metric("Input words",      f"{s['input_words']:,}")
        st.metric("Input characters", f"{s['input_chars']:,}")
        if s.get("est_output_words") is not None:
            st.metric("Est. output words", f"{s['est_output_words']:,}")
            st.metric("Est. output chars", f"{s['est_output_chars']:,}")
        if "output_words" in s:
            st.metric("Actual output words", f"{s['output_words']:,}")
            st.metric("Actual reduction",    f"{s['reduction']:.1f}%")
    else:
        st.caption("Statistics will appear here after loading a source.")

# ── Input area ────────────────────────────────────────────────────────────────
st.subheader("Input Source")
input_mode = st.radio("Choose input mode", ["Upload File", "Enter URL"], horizontal=True)

uploaded_file = None
url_input = ""

if input_mode == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=["txt", "pdf", "doc", "docx", "rtf"],
        help="Supported: .txt · .pdf · .doc · .docx · .rtf",
    )
else:
    url_input = st.text_input(
        "Enter a URL",
        placeholder="https://en.wikipedia.org/wiki/...",
    )

# ── Live input statistics ─────────────────────────────────────────────────────
raw_text = ""
if input_mode == "Upload File" and uploaded_file is not None:
    try:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
        uploaded_file.seek(0)  # reset so parse_input can re-read it later
    except Exception:
        pass
elif input_mode == "Enter URL" and url_input.strip():
    raw_text = st.session_state.get("last_input_body", "")

if raw_text:
    iw = _word_count(raw_text)
    ic = _char_count(raw_text)

    stats: dict = {"input_words": iw, "input_chars": ic}

    if use_target_reduction and reduction_pct is not None:
        est_ow = max(1, int(iw * (1 - reduction_pct / 100)))
        est_oc = max(1, int(ic * (1 - reduction_pct / 100)))
        stats["est_output_words"] = est_ow
        stats["est_output_chars"] = est_oc

    st.session_state.stats = stats

    st.subheader("Input Statistics")
    if use_target_reduction and reduction_pct is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Input words",       f"{iw:,}")
        col2.metric("Input characters",  f"{ic:,}")
        col3.metric("Est. output words", f"{stats['est_output_words']:,}")
        col4.metric("Est. output chars", f"{stats['est_output_chars']:,}")
        st.caption(f"Estimates based on {reduction_pct}% reduction target.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Input words",      f"{iw:,}")
        col2.metric("Input characters", f"{ic:,}")
        st.caption("Output length will be determined automatically by Groq.")

# ── Process button ────────────────────────────────────────────────────────────
st.divider()
run_btn = st.button("Generate Digest", type="primary", use_container_width=True)

if run_btn:
    # Validation
    if not api_key:
        st.error("API key is missing. Add GROQ_API_KEY=your_key to your .env file.")
        st.stop()

    source = uploaded_file if input_mode == "Upload File" else url_input.strip()
    if not source:
        st.error("Please provide a file or URL.")
        st.stop()

    # ── Step 1: Extract text ──────────────────────────────────────────────────
    from input_handler import parse_input
    with st.spinner("Extracting text from source…"):
        try:
            title, body = parse_input(source)
        except Exception as exc:
            st.error(f"Could not extract text: {exc}")
            st.stop()

    # Cache body for URL mode statistics
    st.session_state["last_input_body"] = body
    input_word_count = _word_count(body)
    st.info(f"**Detected title:** {title}")

    # ── Step 2: Summarize via Groq ────────────────────────────────────────────
    from groq_client import summarize
    with st.spinner(f"Generating {chosen_style} digest via Groq AI…"):
        try:
            raw_digest = summarize(title, body, chosen_style, api_key, reduction_pct)
        except Exception as exc:
            st.error(f"Groq API error: {exc}")
            st.stop()

    # ── Step 3: Content filter ────────────────────────────────────────────────
    from content_filter import check_and_clean
    with st.spinner("Checking content safety…"):
        is_safe, digest = check_and_clean(raw_digest)

    if not is_safe:
        st.warning("Some content was filtered for inappropriate language.")

    output_word_count = _word_count(digest)
    reduction = (
        (1 - output_word_count / input_word_count) * 100
        if input_word_count > 0 else 0.0
    )

    # ── Step 4: Save statistics to session state ──────────────────────────────
    post_stats: dict = {
        "input_words":   input_word_count,
        "input_chars":   _char_count(body),
        "output_words":  output_word_count,
        "reduction":     reduction,
    }
    if use_target_reduction and reduction_pct is not None:
        post_stats["est_output_words"] = max(1, int(input_word_count * (1 - reduction_pct / 100)))
        post_stats["est_output_chars"] = max(1, int(_char_count(body) * (1 - reduction_pct / 100)))
    st.session_state.stats = post_stats

    # ── Step 5: Build final text ──────────────────────────────────────────────
    header_line1 = title
    header_line2 = f"Style: {chosen_style.title()}"

    # ── Step 6: Write output file ─────────────────────────────────────────────
    from output_writer import write_output
    with st.spinner(f"Writing {output_format.upper()} file…"):
        try:
            out_path = write_output(header_line1, header_line2, digest, output_format)
        except Exception as exc:
            st.error(f"Could not write output file: {exc}")
            st.stop()

    with open(out_path, "rb") as f:
        file_bytes = f.read()

    # ── Digest preview ────────────────────────────────────────────────────────
    st.subheader("Digest Preview")
    st.text_area(
        label="",
        value=f"{header_line1}\n{header_line2}\n\n{digest}",
        height=300,
        disabled=True,
    )

    st.download_button(
        label=f"Download {output_format.upper()} Digest",
        data=file_bytes,
        file_name=Path(out_path).name,
        mime=_mime_for(output_format),
        use_container_width=True,
    )

    # ── Step 7: Voice reading ─────────────────────────────────────────────────
    if voice_reading:
        from tts_engine import get_audio_bytes
        full_text = f"{header_line1}\n{header_line2}\n\n{digest}"
        with st.spinner("Generating audio…"):
            try:
                audio_bytes = get_audio_bytes(full_text)
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    "Download MP3",
                    data=audio_bytes,
                    file_name="digest_audio.mp3",
                    mime="audio/mpeg",
                )
            except Exception as exc:
                st.warning(f"Voice generation failed: {exc}")

    st.success("Digest complete!")

