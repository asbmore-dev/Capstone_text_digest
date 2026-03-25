# Capstone_text_digest — Complete Reference Guide

> Comprehensive syntax and coding examples to become an expert in every technology used in this project.

---

## Table of Contents

1. [UV Package Manager](#1-uv-package-manager)
2. [Python Fundamentals Used in This Project](#2-python-fundamentals-used-in-this-project)
3. [Streamlit Complete Reference](#3-streamlit-complete-reference)
4. [Groq AI API Reference](#4-groq-ai-api-reference)
5. [File Parsing Libraries](#5-file-parsing-libraries)
6. [Output Format Libraries](#6-output-format-libraries)
7. [gTTS — Text-to-Speech](#7-gtts--text-to-speech)
8. [Content Filtering — better-profanity](#8-content-filtering--better-profanity)
9. [Environment Variables — python-dotenv](#9-environment-variables--python-dotenv)
10. [HTTP Requests & Web Scraping](#10-http-requests--web-scraping)
11. [Python Pathlib & File I/O](#11-python-pathlib--file-io)
12. [pytest — Testing](#12-pytest--testing)
13. [Git & GitHub](#13-git--github)
14. [Python Type Hints & Best Practices](#14-python-type-hints--best-practices)
15. [Error Handling Patterns](#15-error-handling-patterns)

---

## 1. UV Package Manager

UV is a fast, modern Python package manager written in Rust. It replaces pip, venv, and pip-tools.

### Installation

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

### Project lifecycle

```bash
# Create new project (generates pyproject.toml + .venv)
uv init my_project
cd my_project

# Create virtual environment manually
uv venv
uv venv --python 3.11   # specific Python version

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### Dependency management

```bash
# Add a package (updates pyproject.toml + installs)
uv add streamlit
uv add "streamlit>=1.35.0"        # version constraint
uv add --dev pytest               # dev-only dependency
uv add groq python-dotenv pymupdf # multiple at once

# Remove a package
uv remove groq

# Install all deps from pyproject.toml (e.g., after cloning)
uv sync

# Install including dev dependencies
uv sync --extra dev

# List installed packages
uv pip list

# Show package info
uv pip show streamlit

# Export to requirements.txt (for compatibility)
uv pip freeze > requirements.txt
```

### Running commands inside the project environment

```bash
# Run a script
uv run python src/app.py
uv run streamlit run src/app.py
uv run pytest tests/ -v

# Run without activating the venv first
uv run python -c "import streamlit; print(streamlit.__version__)"
```

### pyproject.toml explained

```toml
[project]
name = "my-app"              # package name (hyphens OK)
version = "1.0.0"            # semantic version
description = "Short description"
requires-python = ">=3.11"   # Python version constraint

dependencies = [
    "streamlit>=1.35.0",     # runtime dependency
    "groq>=0.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",         # only installed with: uv sync --extra dev
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]         # lets tests import from src/
```

---

## 2. Python Fundamentals Used in This Project

### Type hints

```python
from __future__ import annotations   # enables postponed evaluation of annotations
from typing import Union, Optional, Tuple

def parse(source: str | bytes) -> tuple[str, str]:
    ...

def maybe_key(x: Optional[str] = None) -> str | None:
    ...

# Built-in generics (Python 3.9+)
def get_chunks(text: str) -> list[str]:
    ...

def route(mapping: dict[str, int]) -> None:
    ...
```

### Dataclasses

```python
from dataclasses import dataclass, field

@dataclass
class DigestResult:
    title: str
    style: str
    body: str
    is_safe: bool = True
    word_count: int = 0

    def __post_init__(self):
        self.word_count = len(self.body.split())

result = DigestResult(title="My Doc", style="modern", body="Hello world")
print(result.word_count)  # → 2
```

### Context managers

```python
# Reading files safely
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("content")     # file closes automatically

# BytesIO — in-memory file object
import io
buf = io.BytesIO()
buf.write(b"hello bytes")
buf.seek(0)                # rewind before reading
data = buf.read()
```

### F-strings (used throughout)

```python
name = "World"
score = 98.6

print(f"Hello, {name}!")                    # Hello, World!
print(f"Score: {score:.1f}")                # Score: 98.6
print(f"Upper: {name.upper()!r}")           # Upper: 'WORLD'
print(f"{'left':<10}{'right':>10}")         # left           right
print(f"{1_000_000:,}")                     # 1,000,000

# Multi-line f-string
html = (
    f"<h1>{name}</h1>\n"
    f"<p>{score}</p>"
)
```

### List comprehensions & generators

```python
# List comprehension
lines = [line.strip() for line in text.splitlines() if line.strip()]

# Dict comprehension
mime_map = {fmt: mime for fmt, mime in [("pdf", "application/pdf"), ("txt", "text/plain")]}

# Generator expression (memory-efficient)
total_chars = sum(len(p.text) for p in doc.paragraphs)

# Conditional comprehension
clean_paras = [p for p in paragraphs if len(p) > 40 and not p.startswith("#")]
```

### Exception handling patterns

```python
# Catch specific exception
try:
    data = extract_from_pdf(file_bytes)
except ImportError as e:
    raise ImportError(f"Missing dependency: {e}") from e
except Exception as e:
    raise RuntimeError(f"PDF extraction failed: {e}") from e

# Multiple exceptions
try:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
except requests.Timeout:
    raise TimeoutError(f"URL {url} timed out after 15 seconds")
except requests.HTTPError as e:
    raise ValueError(f"HTTP {e.response.status_code}: {url}")
except requests.RequestException as e:
    raise ConnectionError(f"Network error: {e}")
```

---

## 3. Streamlit Complete Reference

Streamlit turns Python scripts into web apps with no HTML/CSS/JS required.

### Page setup

```python
import streamlit as st

# Must be the FIRST Streamlit command
st.set_page_config(
    page_title="My App",
    page_icon="📄",           # emoji or URL to image
    layout="wide",            # "centered" (default) or "wide"
    initial_sidebar_state="expanded",   # "auto", "expanded", "collapsed"
    menu_items={
        "Get Help": "https://docs.streamlit.io",
        "Report a bug": "https://github.com/me/repo/issues",
        "About": "# My App\nVersion 1.0",
    }
)
```

### Text display

```python
st.title("Main Title")
st.header("Section Header")
st.subheader("Subsection")
st.text("Monospace fixed text")
st.markdown("**Bold**, *italic*, `code`, [link](https://url)")
st.markdown("---")                  # horizontal rule
st.caption("Small gray caption")
st.code("x = lambda a: a + 1", language="python")
st.latex(r"\sqrt{x^2 + y^2}")
st.divider()                        # horizontal divider (cleaner than ---)

# Display data
st.write("anything")               # smart display — handles str, df, dict, fig...
st.write({"key": "value"})         # displays as JSON
st.json({"nested": {"data": 1}})   # formatted JSON
st.dataframe(df)                   # interactive table
st.table(df)                       # static table
st.metric("Revenue", "$1.2M", "+12%")  # KPI card with delta
```

### Input widgets

```python
# Text input
name = st.text_input("Your name", value="default", placeholder="Type here...")
bio  = st.text_area("Bio", height=150, max_chars=500)

# Numbers
age   = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)
price = st.slider("Price", min_value=0.0, max_value=100.0, value=50.0, step=0.5)
rng   = st.slider("Range", 0, 100, (20, 80))   # range slider → returns tuple

# Selection
choice = st.selectbox("Pick one", ["Option A", "Option B", "Option C"])
multi  = st.multiselect("Pick many", ["A", "B", "C", "D"], default=["A"])
radio  = st.radio("Style", ["Modern", "Classic"], horizontal=True)

# Toggle / checkbox
dark_mode = st.toggle("Dark mode", value=False)
agree     = st.checkbox("I agree to the terms")

# Date / time
import datetime
d = st.date_input("Pick a date", value=datetime.date.today())
t = st.time_input("Pick a time", value=datetime.time(9, 0))

# Color
color = st.color_picker("Brand color", value="#FF5733")

# File uploader
file = st.file_uploader(
    "Upload document",
    type=["txt", "pdf", "docx"],         # allowed extensions
    accept_multiple_files=False,          # True for multi-upload
    help="Max 200MB per file by default",
)
if file:
    bytes_data = file.read()
    st.write(f"Filename: {file.name}, Size: {file.size} bytes")

# Buttons
if st.button("Click me", type="primary", use_container_width=True):
    st.write("Clicked!")

# Download button
with open("report.pdf", "rb") as f:
    st.download_button(
        label="⬇️ Download Report",
        data=f,
        file_name="report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# Direct bytes download (no file needed on disk)
st.download_button("Download", data=b"hello bytes", file_name="hello.txt")
```

### Layout & containers

```python
# Columns
col1, col2, col3 = st.columns(3)
col1, col2 = st.columns([2, 1])        # ratio: col1 is 2x wider

with col1:
    st.header("Left")
col2.write("Right")                    # dot notation also works

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("API Key", type="password")

# Expander
with st.expander("Advanced Options", expanded=False):
    verbose = st.checkbox("Verbose output")

# Tabs
tab1, tab2, tab3 = st.tabs(["Summary", "Details", "Raw Text"])
with tab1:
    st.write("Summary content")
with tab2:
    st.write("Detailed content")

# Container (groups elements, can be cleared)
container = st.container()
container.write("This can be rewritten later")
container.empty()                      # clears the container

placeholder = st.empty()
placeholder.text("Loading...")
# later:
placeholder.text_area("Result", value="done", height=200)

# Status / progress
with st.spinner("Processing..."):
    import time; time.sleep(2)         # long operation

progress = st.progress(0, text="Starting...")
for i in range(100):
    progress.progress(i + 1, text=f"Step {i+1}/100")

st.balloons()     # 🎈 celebration animation
st.snow()         # ❄️ snow animation
```

### State management

```python
# Session state persists across reruns within one session
if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write(f"Count: {st.session_state.count}")

# Store complex objects
if "history" not in st.session_state:
    st.session_state.history = []

st.session_state.history.append("new item")

# Callback pattern (widget callbacks)
def on_style_change():
    st.session_state.needs_refresh = True

st.selectbox("Style", ["modern", "classic"], on_change=on_style_change)
```

### Caching (performance)

```python
# Cache a function that returns data (recomputes only when args change)
@st.cache_data
def load_big_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# Cache a resource (DB connections, ML models — shared across sessions)
@st.cache_resource
def get_groq_client(api_key: str):
    from groq import Groq
    return Groq(api_key=api_key)

# Clear cache manually
load_big_file.clear()
st.cache_data.clear()
```

### Media

```python
# Images
st.image("logo.png", width=200, caption="Logo")
st.image("https://url.com/img.jpg", use_column_width=True)

# Audio
st.audio("speech.mp3")
st.audio(mp3_bytes, format="audio/mp3")   # from bytes
st.audio(wav_bytes, format="audio/wav")

# Video
st.video("demo.mp4")
st.video("https://youtube.com/watch?v=...")
```

### Notifications & feedback

```python
st.success("✅ Operation completed!")
st.error("❌ Something went wrong.")
st.warning("⚠️ Check your input.")
st.info("ℹ️ For your information.")
st.exception(e)                     # display a Python exception nicely

# Toast notification (bottom-right popup)
st.toast("Saved!", icon="💾")
```

---

## 4. Groq AI API Reference

Groq provides a free tier for their LLM inference API with extremely fast throughput.

### Setup

```bash
uv add groq
```

```python
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
```

### Basic completion

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain gravity in one sentence."},
    ],
    temperature=0.7,
    max_tokens=512,
)

text = response.choices[0].message.content
print(text)
```

### Message roles explained

```python
messages = [
    # system: instructions / persona for the AI (set at start)
    {"role": "system", "content": "You are a professional editor."},

    # user: what the human says
    {"role": "user", "content": "Summarize this article: ..."},

    # assistant: what the AI previously said (for multi-turn)
    {"role": "assistant", "content": "Here is the summary: ..."},

    # continue the conversation
    {"role": "user", "content": "Make it shorter."},
]
```

### Model parameters

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",

    # Controls randomness (0.0 = deterministic, 2.0 = very random)
    temperature=0.6,

    # Max tokens in the response
    max_tokens=1024,

    # Nucleus sampling — alternative to temperature (0–1)
    # 0.9 means "consider tokens comprising top 90% of probability mass"
    top_p=0.9,

    # Penalize repeating tokens already in the response (-2 to 2)
    frequency_penalty=0.0,

    # Penalize tokens that appeared in the prompt (-2 to 2)
    presence_penalty=0.0,

    # Stop generation when this string is encountered
    stop=["\n\n", "END"],

    # Stream tokens as they're generated
    stream=False,
)
```

### Available free models (2025)

```python
# Fastest — best for summarization tasks
model = "llama-3.1-8b-instant"

# More capable — better for complex tasks
model = "llama-3.3-70b-versatile"

# Google's Gemma 2
model = "gemma2-9b-it"

# Long context (32k tokens)
model = "mixtral-8x7b-32768"
```

### Streaming responses

```python
stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Tell me a long story."}],
    stream=True,
)

full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content or ""
    full_response += delta
    print(delta, end="", flush=True)
```

### Streaming in Streamlit

```python
# Display Groq response as it streams into a Streamlit text area
placeholder = st.empty()
full_text = ""

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content or ""
    full_text += delta
    placeholder.markdown(full_text + "▌")   # cursor effect

placeholder.markdown(full_text)             # final version without cursor
```

### Error handling

```python
from groq import APIConnectionError, RateLimitError, APIStatusError

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    print("Rate limit hit — wait and retry")
except APIConnectionError:
    print("Network error — check internet connection")
except APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### Token counting tip

```python
# Rough estimate: 1 token ≈ 4 characters in English
# Free tier limits vary; check console.groq.com for current limits
# llama-3.1-8b-instant context window: 128k tokens

def estimate_tokens(text: str) -> int:
    return len(text) // 4
```

---

## 5. File Parsing Libraries

### PyMuPDF (PDF extraction)

```bash
uv add pymupdf
```

```python
import fitz   # PyMuPDF's import name is 'fitz'
import io

# Open from bytes (from Streamlit UploadedFile)
data = uploaded_file.read()
doc = fitz.open(stream=data, filetype="pdf")

# Open from file path
doc = fitz.open("document.pdf")

# Iterate pages
for page_num, page in enumerate(doc):
    text = page.get_text()                # plain text
    blocks = page.get_text("blocks")      # list of (x0,y0,x1,y1,text,...) tuples
    words = page.get_text("words")        # word-level extraction

# Full document text
full_text = "\n\n".join(page.get_text() for page in doc)

# Page count
print(f"Pages: {doc.page_count}")

# Document metadata
meta = doc.metadata
print(meta["title"], meta["author"])

# Extract images from a page
for img in page.get_images():
    xref = img[0]
    image = doc.extract_image(xref)
    img_bytes = image["image"]            # raw bytes

doc.close()
```

### python-docx (Word documents)

```bash
uv add python-docx
```

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# ── Reading ───────────────────────────────────────────────────────
doc = Document(io.BytesIO(file_bytes))     # from bytes
doc = Document("document.docx")            # from path

# Paragraphs
for para in doc.paragraphs:
    print(para.text)
    print(para.style.name)                 # e.g. "Heading 1", "Normal"

# Tables
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)

# All text at once
full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

# ── Writing ───────────────────────────────────────────────────────
doc = Document()

# Headings (level 1–6)
doc.add_heading("Document Title", level=1)
doc.add_heading("Section Header", level=2)

# Paragraphs
para = doc.add_paragraph("Regular paragraph text.")

# Styled runs within a paragraph
para = doc.add_paragraph()
run = para.add_run("Bold text")
run.bold = True
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)   # hex color

# Italic
para.add_run(" and ").italic = True
para.add_run("normal").bold = False

# Alignment
para.alignment = WD_ALIGN_PARAGRAPH.CENTER
# WD_ALIGN_PARAGRAPH.LEFT / RIGHT / JUSTIFY

# Page break
doc.add_page_break()

# Table
table = doc.add_table(rows=2, cols=3)
table.style = "Table Grid"
table.cell(0, 0).text = "Header 1"
table.cell(0, 1).text = "Header 2"
table.cell(0, 2).text = "Header 3"

# Save
doc.save("output.docx")

# Save to bytes (for Streamlit download)
buf = io.BytesIO()
doc.save(buf)
docx_bytes = buf.getvalue()
```

### striprtf (RTF extraction)

```bash
uv add striprtf
```

```python
from striprtf.striprtf import rtf_to_text

# From bytes
rtf_bytes = uploaded_file.read()
rtf_string = rtf_bytes.decode("latin-1", errors="replace")

plain_text = rtf_to_text(rtf_string)

# Note: RTF files are often encoded in latin-1, not UTF-8
# Always use errors="replace" to handle problem bytes
```

### Writing RTF manually

```python
def write_rtf(title: str, body: str) -> str:
    """Escape and write a minimal valid RTF 1.5 file."""
    def esc(text: str) -> str:
        out = []
        for ch in text:
            if ord(ch) < 128:
                if ch in ("\\", "{", "}"):
                    out.append("\\" + ch)
                else:
                    out.append(ch)
            else:
                out.append(f"\\u{ord(ch)}?")
        return "".join(out)

    return (
        r"{\rtf1\ansi\deff0"
        r"{\fonttbl{\f0 Times New Roman;}}"
        "\n"
        r"{\pard\fs32\b " + esc(title) + r"\b0\par}"
        "\n"
        r"{\pard\fs24 " + esc(body).replace("\n", r"\par ") + r"\par}"
        "\n}"
    )
```

---

## 6. Output Format Libraries

### fpdf2 (PDF generation)

```bash
uv add fpdf2
```

```python
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Fonts: Helvetica, Times, Courier (built-in, no embedding needed)
# Styles: "" (normal), "B" (bold), "I" (italic), "U" (underline), "BI"

# Title
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Document Title", ln=True)

# Subtitle
pdf.set_font("Helvetica", "I", 11)
pdf.cell(0, 8, "Style: Modern", ln=True)
pdf.ln(6)                                 # 6mm vertical space

# Body — multi_cell wraps text automatically
pdf.set_font("Helvetica", size=11)
pdf.multi_cell(0, 7, "Long body text that will wrap automatically...")

# Add an image
pdf.image("logo.png", x=10, y=10, w=30)  # x,y in mm, w=width

# Colors
pdf.set_text_color(0, 0, 128)             # RGB — navy text
pdf.set_fill_color(230, 230, 230)         # light gray fill
pdf.set_draw_color(200, 200, 200)         # gray border

# Colored cell
pdf.set_fill_color(52, 73, 94)            # dark blue
pdf.set_text_color(255, 255, 255)         # white text
pdf.cell(0, 12, "Highlighted cell", fill=True, ln=True)

# Reset colors
pdf.set_text_color(0, 0, 0)
pdf.set_fill_color(255, 255, 255)

# Page number in footer
class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# Save
pdf.output("output.pdf")

# Save to bytes
import io
buf = io.BytesIO()
pdf.output(buf)
pdf_bytes = buf.getvalue()
```

### HTML generation

```python
def render_html(title: str, style_label: str, body: str) -> str:
    # Escape special HTML characters
    def esc(text: str) -> str:
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

    body_html = esc(body).replace("\n\n", "</p>\n<p>").replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <style>
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      max-width: 780px;
      margin: 48px auto;
      padding: 0 24px;
      color: #1a1a1a;
      line-height: 1.75;
      background: #fafaf8;
    }}
    h1  {{ font-size: 2rem; margin-bottom: 4px; color: #111; }}
    .style-label {{
      color: #777; font-style: italic;
      font-size: 0.9rem; margin-bottom: 2rem;
    }}
    p   {{ margin: 0 0 1.2em; text-indent: 1.5em; }}
    p:first-of-type {{ text-indent: 0; }}
  </style>
</head>
<body>
  <h1>{esc(title)}</h1>
  <p class="style-label">{esc(style_label)}</p>
  <p>{body_html}</p>
</body>
</html>"""
```

---

## 7. gTTS — Text-to-Speech

gTTS (Google Text-to-Speech) uses Google's TTS engine. It's free and requires no API key, but needs an internet connection.

```bash
uv add gtts
```

### Basic usage

```python
from gtts import gTTS
import io

# Simplest usage — save to file
tts = gTTS(text="Hello, world!", lang="en")
tts.save("output.mp3")

# Get bytes (for Streamlit or in-memory use)
tts = gTTS(text="Hello, world!", lang="en", slow=False)
buf = io.BytesIO()
tts.write_to_fp(buf)
audio_bytes = buf.getvalue()

# Play in Streamlit
import streamlit as st
st.audio(audio_bytes, format="audio/mp3")
```

### Language codes

```python
# Common language codes for gTTS
LANGUAGES = {
    "en":    "English",
    "es":    "Spanish",
    "fr":    "French",
    "de":    "German",
    "it":    "Italian",
    "pt":    "Portuguese",
    "ja":    "Japanese",
    "ko":    "Korean",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "ru":    "Russian",
    "ar":    "Arabic",
    "hi":    "Hindi",
    "nl":    "Dutch",
    "pl":    "Polish",
    "sv":    "Swedish",
}

# List all available languages
from gtts.lang import tts_langs
all_langs = tts_langs()       # returns dict of code → name
```

### Chunking long text

```python
def text_to_speech_chunked(text: str, lang: str = "en") -> bytes:
    """Handle texts longer than gTTS's ~5000 char soft limit."""
    MAX = 4000
    sentences = text.replace("\n", " ").split(". ")

    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < MAX:
            current += s + ". "
        else:
            if current:
                chunks.append(current.strip())
            current = s + ". "
    if current:
        chunks.append(current.strip())

    buf = io.BytesIO()
    for chunk in chunks:
        gTTS(text=chunk, lang=lang).write_to_fp(buf)

    return buf.getvalue()
```

### TLD variants (different accents)

```python
# Use 'tld' parameter for regional accents
tts = gTTS("Hello!", lang="en", tld="com")    # US English
tts = gTTS("Hello!", lang="en", tld="co.uk")  # British English
tts = gTTS("Hello!", lang="en", tld="com.au") # Australian English
tts = gTTS("Bonjour!", lang="fr", tld="fr")   # French from France
tts = gTTS("Hola!", lang="es", tld="es")      # Spanish from Spain
```

---

## 8. Content Filtering — better-profanity

```bash
uv add better-profanity
```

```python
from better_profanity import profanity

# Load default word list (must call before using)
profanity.load_censor_words()

# Check
profanity.contains_profanity("Hello world!")     # → False
profanity.contains_profanity("You bad person!")  # → True (if "bad" in list)

# Censor (replace with asterisks by default)
profanity.censor("This is a bad word")           # → "This is a *** word"
profanity.censor("This is bad", censor_char="-") # → "This is ---"

# Add custom words
profanity.add_censor_words(["spam", "junk", "garbage"])

# Load a completely custom word list from a file
# (one word per line)
profanity.load_censor_words_from_file("my_words.txt")

# Check with custom list only
profanity.load_censor_words(whitelist_words=["hello"])  # whitelist 'hello'

# Practical content filter
def content_is_safe(text: str) -> bool:
    return not profanity.contains_profanity(text)

def safe_text(text: str) -> tuple[bool, str]:
    if profanity.contains_profanity(text):
        return False, profanity.censor(text)
    return True, text
```

---

## 9. Environment Variables — python-dotenv

```bash
uv add python-dotenv
```

```python
# ── .env file format ──────────────────────────────────────────────
# GROQ_API_KEY=gsk_abc123
# DEBUG=true
# MAX_TOKENS=1024
# APP_NAME=Capstone Text Digest

# ── Loading in Python ─────────────────────────────────────────────
from dotenv import load_dotenv
import os

load_dotenv()               # reads .env from current dir or parent dirs
load_dotenv(".env.prod")    # load a specific file

key = os.getenv("GROQ_API_KEY")                    # None if missing
key = os.getenv("GROQ_API_KEY", "default-value")   # with fallback
key = os.environ["GROQ_API_KEY"]                   # raises KeyError if missing

# ── Validation pattern ────────────────────────────────────────────
def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            f"Copy .env.example to .env and fill in your values."
        )
    return value

api_key = get_required_env("GROQ_API_KEY")

# ── Type conversion ───────────────────────────────────────────────
debug = os.getenv("DEBUG", "false").lower() == "true"
max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
```

### Streamlit Secrets (alternative to .env for deployment)

```toml
# .streamlit/secrets.toml  ← never commit this file!
GROQ_API_KEY = "gsk_abc123"
```

```python
# Access in Streamlit
api_key = st.secrets["GROQ_API_KEY"]

# Check if key exists
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
```

---

## 10. HTTP Requests & Web Scraping

### requests

```bash
uv add requests
```

```python
import requests

# Basic GET
resp = requests.get("https://example.com", timeout=15)
resp.raise_for_status()       # raises HTTPError for 4xx/5xx

text = resp.text              # response body as string
data = resp.json()            # parse JSON body
raw  = resp.content           # response body as bytes
code = resp.status_code       # e.g. 200

# With headers (important for scraping — avoid bot detection)
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; MyBot/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}
resp = requests.get(url, headers=headers, timeout=15)

# POST request
resp = requests.post(
    "https://api.example.com/data",
    json={"key": "value"},          # auto-sets Content-Type: application/json
    headers={"Authorization": f"Bearer {token}"},
)

# Session (reuses TCP connection, persists cookies)
session = requests.Session()
session.headers.update({"User-Agent": "MyBot"})
resp1 = session.get("https://example.com/login")
resp2 = session.get("https://example.com/data")   # same session
```

### BeautifulSoup4 (HTML parsing)

```bash
uv add beautifulsoup4 lxml
```

```python
from bs4 import BeautifulSoup
import requests

resp = requests.get("https://en.wikipedia.org/wiki/Python_(programming_language)")
soup = BeautifulSoup(resp.text, "lxml")     # lxml is faster than html.parser

# Find single element
h1    = soup.find("h1")
title = h1.get_text(strip=True) if h1 else "No title"

# Find all matching elements
paragraphs = soup.find_all("p")
texts = [p.get_text(separator=" ", strip=True) for p in paragraphs]

# CSS selectors (more expressive)
main_content = soup.select_one("div#mw-content-text")
links = soup.select("a[href^='/wiki/']")     # all wiki links

# Attribute access
link = soup.find("a", href=True)
url  = link["href"]
text = link.get_text()

# Remove unwanted elements
for tag in soup(["script", "style", "nav", "footer", "aside"]):
    tag.decompose()

# Extract all text
all_text = soup.get_text(separator="\n", strip=True)

# Filtering by class or id
div = soup.find("div", class_="article-body")
div = soup.find("div", id="main-content")
```

---

## 11. Python Pathlib & File I/O

```python
from pathlib import Path
import shutil

# ── Creating paths ────────────────────────────────────────────────
p = Path("output_files/digest.txt")
p = Path.home() / "Documents" / "digest.txt"  # ~ expansion
p = Path(__file__).parent / "assets"           # relative to current script

# ── Reading ───────────────────────────────────────────────────────
text  = p.read_text(encoding="utf-8")
raw   = p.read_bytes()

# ── Writing ───────────────────────────────────────────────────────
p.write_text("content", encoding="utf-8")
p.write_bytes(b"\x89PNG\r\n")

# Append (write_text can't append; use open())
with p.open("a", encoding="utf-8") as f:
    f.write("appended line\n")

# ── Directory operations ──────────────────────────────────────────
p.mkdir(parents=True, exist_ok=True)   # create directory tree
p.parent.mkdir(exist_ok=True)          # ensure parent exists

for child in p.iterdir():              # list directory contents
    print(child.name, child.is_file(), child.is_dir())

for f in p.glob("*.txt"):              # glob pattern
    print(f)

for f in p.rglob("**/*.py"):           # recursive glob
    print(f)

# ── Inspection ───────────────────────────────────────────────────
p.exists()                  # True / False
p.is_file()
p.is_dir()
p.stat().st_size            # file size in bytes
p.suffix                    # ".txt"
p.stem                      # "digest" (no extension)
p.name                      # "digest.txt"
p.parent                    # Path object of parent directory

# ── Copy / move / delete ─────────────────────────────────────────
shutil.copy(src, dst)       # copy file
shutil.move(src, dst)       # move/rename file
p.unlink()                  # delete file
shutil.rmtree(dir_path)     # delete directory tree

# ── Timestamp-based unique names ─────────────────────────────────
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out = Path("output_files") / f"digest_{stamp}.pdf"
```

---

## 12. pytest — Testing

```bash
uv add --dev pytest pytest-mock
```

### Test file structure

```python
# tests/test_my_module.py
# Convention: file starts with 'test_', function starts with 'test_'

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from my_module import my_function

class TestMyFunction:
    """Group related tests in a class."""

    def test_basic_case(self):
        result = my_function("hello")
        assert result == "HELLO"

    def test_empty_string(self):
        result = my_function("")
        assert result == ""

    def test_returns_string(self):
        result = my_function("test")
        assert isinstance(result, str)
```

### Assertions

```python
# Equality
assert x == 42
assert x != 0
assert x is None
assert x is not None

# Collections
assert "key" in my_dict
assert item in my_list
assert len(my_list) == 3

# Approximate equality (for floats)
import pytest
assert result == pytest.approx(3.14, abs=0.01)

# Exceptions
with pytest.raises(ValueError):
    raise ValueError("bad input")

with pytest.raises(ValueError, match="bad input"):
    raise ValueError("bad input")
```

### Fixtures

```python
import pytest

@pytest.fixture
def sample_text():
    return "The Great Gatsby\n\nIn my younger and more vulnerable years..."

@pytest.fixture
def groq_client(mocker):
    """Mock Groq client so tests don't make real API calls."""
    mock = mocker.MagicMock()
    mock.chat.completions.create.return_value.choices[0].message.content = "Summary."
    return mock

def test_summarize(sample_text, groq_client):
    # Use the fixture values
    assert len(sample_text) > 0
```

### Mocking

```python
from unittest.mock import patch, MagicMock, call

# Patch at the point of use (not definition)
@patch("groq_client.Groq")             # patches Groq where it's imported in groq_client.py
def test_api_call(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test digest."
    mock_client.chat.completions.create.return_value = mock_response

    from groq_client import summarize
    result = summarize("Title", "Body", "modern", "fake-key")
    assert result == "Test digest."

# Verify the mock was called correctly
mock_client.chat.completions.create.assert_called_once()
args, kwargs = mock_client.chat.completions.create.call_args
assert kwargs["model"] == "llama-3.1-8b-instant"

# Patch as context manager
with patch("requests.get") as mock_get:
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html><p>Hello</p></html>"
    # ... test code
```

### Parametrize

```python
@pytest.mark.parametrize("style,expected_keyword", [
    ("modern",       "contemporary"),
    ("humorous",     "humor"),
    ("professional", "formal"),
    ("academic",     "scholarly"),
])
def test_build_prompt_includes_style_instruction(style, expected_keyword):
    from groq_client import build_prompt
    prompt = build_prompt("Test Title", "Test body.", style)
    assert expected_keyword in prompt.lower()
```

### Running tests

```bash
uv run pytest                        # run all tests
uv run pytest tests/ -v              # verbose
uv run pytest tests/test_file.py     # single file
uv run pytest -k "test_title"        # tests matching pattern
uv run pytest --tb=short             # shorter traceback
uv run pytest -x                     # stop on first failure
uv run pytest --cov=src              # coverage report (needs pytest-cov)
```

---

## 13. Git & GitHub

### Initial setup

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

### Daily workflow

```bash
# Initialize
git init
git add .
git commit -m "feat: initial implementation"

# Status and diff
git status
git diff                    # unstaged changes
git diff --staged           # staged changes

# Stage and commit
git add src/app.py          # stage specific file
git add .                   # stage all changes
git commit -m "fix: handle empty PDF"

# Undo
git restore src/app.py      # discard unstaged changes
git restore --staged src/   # unstage (keep changes)
git commit --amend          # edit last commit message

# Branches
git branch feature/voice-output     # create
git checkout feature/voice-output   # switch
git checkout -b feature/new-thing   # create + switch
git merge feature/voice-output      # merge into current branch
git branch -d feature/voice-output  # delete merged branch
```

### Remote (GitHub)

```bash
# First push
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main

# Subsequent pushes
git push

# Pull latest
git pull

# Clone
git clone https://github.com/USERNAME/Capstone_text_digest.git
cd Capstone_text_digest
```

### Commit message conventions

```
type(scope): short description (50 chars max)

[optional body — explain WHY, not WHAT]

[optional footer: BREAKING CHANGE, Fixes #123]
```

```bash
# Types:
feat:     new feature
fix:      bug fix
docs:     documentation only
style:    formatting (no logic change)
refactor: code restructuring
test:     adding/updating tests
chore:    build process, dependencies
ci:       CI/CD changes
perf:     performance improvements

# Examples:
git commit -m "feat: add RTF output format"
git commit -m "fix: handle empty PDF extraction gracefully"
git commit -m "docs: update README with installation steps"
git commit -m "test: add unit tests for content_filter"
```

### GitHub Actions CI (optional)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v3

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Run tests
        run: uv run pytest tests/ -v
```

---

## 14. Python Type Hints & Best Practices

### Type hints

```python
from __future__ import annotations
from typing import Union, Optional, Any
from collections.abc import Callable, Generator, Iterator

# Basic
def greet(name: str) -> str:
    return f"Hello, {name}"

# Union types (Python 3.10+ shorthand)
def process(data: str | bytes | None) -> str:
    ...

# Optional = X | None
def find(key: str) -> Optional[str]:
    ...

# Complex types
def transform(items: list[tuple[str, int]]) -> dict[str, int]:
    ...

# Callable
def apply(func: Callable[[str], str], text: str) -> str:
    return func(text)

# TypeAlias (Python 3.10+)
from typing import TypeAlias
FilePath: TypeAlias = str | Path

# Literal types
from typing import Literal
OutputFormat = Literal["txt", "pdf", "docx", "rtf", "html"]

def write(text: str, fmt: OutputFormat) -> None:
    ...
```

### Best practices applied in this project

```python
# ── Use __all__ to define public API ─────────────────────────────
__all__ = ["parse_input", "detect_title"]

# ── Docstrings ────────────────────────────────────────────────────
def summarize(title: str, body: str, style: str, api_key: str) -> str:
    """
    Summarize text using Groq AI with a chosen style.

    Args:
        title:   Detected title of the source document.
        body:    Main text (truncated to 12k chars if needed).
        style:   Style keyword (modern, humorous, etc.) or custom string.
        api_key: Valid Groq API key.

    Returns:
        Digest string without title.

    Raises:
        groq.APIConnectionError: If network is unavailable.
        groq.RateLimitError: If free tier limit is exceeded.
    """

# ── Constants at module level ─────────────────────────────────────
MAX_BODY_CHARS = 12_000
DEFAULT_STYLE  = "modern"
OUTPUT_DIR     = Path(__file__).parent.parent / "output_files"

# ── Early returns (avoid deep nesting) ───────────────────────────
def process(text: str) -> str:
    if not text:
        return ""
    if len(text) < 10:
        return text
    # main logic here
    return text.upper()

# ── Guard clauses ─────────────────────────────────────────────────
def write_output(body: str, fmt: str) -> str:
    if not body:
        raise ValueError("Body text cannot be empty.")
    if fmt not in {"txt", "pdf", "docx", "rtf", "html"}:
        raise ValueError(f"Unsupported format: {fmt!r}")
    # proceed with valid inputs...
```

---

## 15. Error Handling Patterns

### Graceful degradation in Streamlit

```python
# Pattern used in app.py
try:
    result = risky_operation()
except SpecificError as e:
    st.error(f"Operation failed: {e}")
    st.stop()       # halt the current script run
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.exception(e)  # shows full traceback in the UI
    st.stop()
```

### Retry logic

```python
import time
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator that retries a function on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2.0)
def call_groq_api(prompt: str) -> str:
    ...
```

### Logging

```python
import logging

# Configure once at app startup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),                      # console
        logging.FileHandler("app.log", encoding="utf-8"),  # file
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.debug("Detailed debug info: %s", value)
logger.info("Processing file: %s", filename)
logger.warning("File was empty, using fallback.")
logger.error("Groq API call failed: %s", exc)
logger.exception("Unexpected error:")   # includes traceback
```

---

## Quick Lookup — Import Map

| What you need | Import |
|---|---|
| Groq AI client | `from groq import Groq` |
| Streamlit | `import streamlit as st` |
| Load .env | `from dotenv import load_dotenv` |
| Environment var | `import os; os.getenv("KEY")` |
| PDF extraction | `import fitz` (PyMuPDF) |
| Word doc read/write | `from docx import Document` |
| RTF extraction | `from striprtf.striprtf import rtf_to_text` |
| HTTP request | `import requests` |
| HTML parse | `from bs4 import BeautifulSoup` |
| Write PDF | `from fpdf import FPDF` |
| TTS audio | `from gtts import gTTS` |
| Profanity filter | `from better_profanity import profanity` |
| File paths | `from pathlib import Path` |
| In-memory file | `import io; io.BytesIO()` |
| Date/time | `from datetime import datetime` |
| Mock in tests | `from unittest.mock import patch, MagicMock` |
| pytest fixtures | `import pytest` |
