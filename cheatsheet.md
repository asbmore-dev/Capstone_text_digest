# Capstone_text_digest — Cheat Sheet

> Quick-reference card for daily development. Keep this open while coding.

---

## ⚡ Run Commands

```bash
# Start the app
uv run streamlit run src/app.py

# Start on custom port
uv run streamlit run src/app.py --server.port 8502

# Run tests
uv run pytest tests/ -v

# Run single test file
uv run pytest tests/test_input_handler.py -v

# Install a new package
uv add <package-name>

# Install dev dependency
uv add --dev <package-name>

# Sync all dependencies
uv sync

# Show installed packages
uv pip list
```

---

## 📁 Key Files

| File | Purpose |
|---|---|
| `src/app.py` | Streamlit UI — edit to change the interface |
| `src/groq_client.py` | Change the AI model or prompt here |
| `src/content_filter.py` | Adjust profanity rules here |
| `src/output_writer.py` | Add new output formats here |
| `src/tts_engine.py` | Change TTS language/speed here |
| `.env` | API keys — **never commit!** |

---

## 🔑 Environment

```bash
# .env file format
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# Load in Python
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv("GROQ_API_KEY")
```

---

## 🤖 Groq API

```python
from groq import Groq

client = Groq(api_key="gsk_...")

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",   # free
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "Summarize this text: ..."}
    ],
    temperature=0.6,   # 0=deterministic, 1=creative
    max_tokens=1024,
)

digest = response.choices[0].message.content
```

**Free Groq models:**
- `llama-3.1-8b-instant` — fastest, best for summarization
- `gemma2-9b-it` — Google's Gemma 2
- `mixtral-8x7b-32768` — longer context window

---

## 🎨 Streamlit Snippets

```python
import streamlit as st

# Page config (must be FIRST st call)
st.set_page_config(page_title="My App", page_icon="📄", layout="wide")

# Text elements
st.title("Title")
st.header("Header")
st.subheader("Subheader")
st.text("Plain text")
st.markdown("**Bold** and *italic*")
st.caption("Small caption")
st.code("print('hello')", language="python")

# Input widgets
file = st.file_uploader("Upload", type=["txt","pdf"])
url  = st.text_input("URL", placeholder="https://...")
style = st.selectbox("Style", ["modern","humorous"])
toggle = st.toggle("Enable voice", value=False)
btn  = st.button("Run", type="primary")

# Layout
col1, col2 = st.columns(2)
with col1:
    st.write("Left column")

with st.sidebar:
    st.header("Settings")

# Feedback
st.success("Done!")
st.error("Something went wrong.")
st.warning("Check this.")
st.info("FYI...")

with st.spinner("Loading…"):
    pass   # long operation here

# Display results
st.text_area("Preview", value="text", height=300)
st.audio(mp3_bytes, format="audio/mp3")

# Download
with open("file.pdf", "rb") as f:
    st.download_button("Download PDF", f, "output.pdf", "application/pdf")

# Stop execution
st.stop()
```

---

## 📄 File Parsing

```python
# ── TXT ──────────────────────────────────────────────────────────
text = uploaded_file.read().decode("utf-8", errors="replace")

# ── PDF (PyMuPDF) ─────────────────────────────────────────────────
import fitz
doc = fitz.open(stream=file_bytes, filetype="pdf")
text = "\n".join(page.get_text() for page in doc)

# ── DOCX ─────────────────────────────────────────────────────────
from docx import Document
import io
doc = Document(io.BytesIO(file_bytes))
text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

# ── RTF ───────────────────────────────────────────────────────────
from striprtf.striprtf import rtf_to_text
text = rtf_to_text(rtf_string)

# ── URL ───────────────────────────────────────────────────────────
import requests
from bs4 import BeautifulSoup
resp = requests.get(url, timeout=15)
soup = BeautifulSoup(resp.text, "lxml")
text = " ".join(p.get_text() for p in soup.find_all("p"))
```

---

## 🔒 Content Filter

```python
from better_profanity import profanity

profanity.load_censor_words()

profanity.contains_profanity("hello world")  # → False
profanity.censor("bad word here", "*")       # → "*** **** here"
profanity.add_censor_words(["custom", "words"])
```

---

## 🔊 Text-to-Speech (gTTS)

```python
from gtts import gTTS
import io

tts = gTTS(text="Hello, world!", lang="en", slow=False)

# Save to file
tts.save("output.mp3")

# Get bytes for Streamlit
buf = io.BytesIO()
tts.write_to_fp(buf)
audio_bytes = buf.getvalue()

st.audio(audio_bytes, format="audio/mp3")

# Language codes
# en=English, es=Spanish, fr=French, de=German
# ja=Japanese, zh-cn=Chinese, pt=Portuguese, it=Italian
```

---

## 📝 Write Output Files

```python
# ── TXT ──────────────────────────────────────────────────────────
from pathlib import Path
Path("output.txt").write_text("content", encoding="utf-8")

# ── PDF (fpdf2) ───────────────────────────────────────────────────
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Title", ln=True)
pdf.set_font("Helvetica", size=11)
pdf.multi_cell(0, 7, "Body text...")
pdf.output("output.pdf")

# ── DOCX ─────────────────────────────────────────────────────────
from docx import Document
from docx.shared import Pt
doc = Document()
doc.add_heading("Title", level=1)
p = doc.add_paragraph("Style subtitle")
p.runs[0].italic = True
doc.add_paragraph("Body text here.")
doc.save("output.docx")

# ── HTML ──────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html><head><title>{title}</title></head>
<body><h1>{title}</h1><p>{body}</p></body></html>"""
Path("output.html").write_text(html, encoding="utf-8")
```

---

## 🧪 Pytest Quick Reference

```python
# Basic test
def test_something():
    assert 1 + 1 == 2

# Test with exception
import pytest
def test_raises():
    with pytest.raises(ValueError):
        raise ValueError("oops")

# Mock a function
from unittest.mock import patch, MagicMock

@patch("module.ClassName")
def test_with_mock(mock_class):
    mock_instance = MagicMock()
    mock_class.return_value = mock_instance
    mock_instance.some_method.return_value = "fake result"
    # ... your test code

# Run specific test
# uv run pytest tests/test_file.py::TestClass::test_method -v
```

---

## 🚀 Git + GitHub Workflow

```bash
# First push
git init
git add .
git commit -m "feat: initial implementation"
gh repo create Capstone_text_digest --public --source=. --remote=origin
git push -u origin main

# Daily workflow
git add .
git commit -m "fix: handle empty PDF pages"
git push

# Good commit message prefixes
# feat:  new feature
# fix:   bug fix
# docs:  documentation change
# test:  adding tests
# refactor: code cleanup
```

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: groq` | `uv add groq` |
| `ModuleNotFoundError: fitz` | `uv add pymupdf` |
| `AuthenticationError` from Groq | Check `.env` has valid `GROQ_API_KEY` |
| `OSError: [Errno 99]` from gTTS | No internet connection |
| Streamlit port 8501 in use | `--server.port 8502` |
| `UnicodeDecodeError` on txt file | Use `errors="replace"` in `.decode()` |
| Empty PDF extraction | File is likely a scanned image (needs OCR) |
