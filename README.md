# 📄 Capstone Text Digest

> **Transform any document into a polished, styled summary — with voice reading.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Free_Tier-orange)](https://console.groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Features

| Feature | Details |
|---|---|
| **Input formats** | `.txt` · `.pdf` · `.doc/.docx` · `.rtf` · HTTP URL |
| **Output formats** | `.txt` · `.pdf` · `.docx` · `.rtf` · `.html` |
| **AI engine** | Groq `llama-3.1-8b-instant` (free, no credit card) |
| **Style adaptation** | original · modern · humorous · professional · academic · custom |
| **Content safety** | Automatic profanity filter with `better-profanity` |
| **Voice reading** | gTTS MP3 generation (free, no API key) |
| **Output header** | Line 1: original title · Line 2: style used |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) package manager
- Free [Groq API key](https://console.groq.com)

### 2. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/Capstone_text_digest.git
cd Capstone_text_digest
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env and paste your Groq API key
```

### 4. Run

```bash
uv run streamlit run src/app.py
```

Open **http://localhost:8501** in your browser.

---

## Flowchart

See [`docs/flowchart.md`](docs/flowchart.md) for the full Mermaid diagram.

```
Input (txt/pdf/docx/rtf/URL)
    ↓
Text Extraction
    ↓
Groq AI Summarization (styled)
    ↓
Content Safety Filter
    ↓
Output File (txt/pdf/docx/rtf/html)
    ↓
Optional: Voice Reading (MP3)
```

---

## Project Structure

```
Capstone_text_digest/
├── src/
│   ├── app.py              # Streamlit UI
│   ├── input_handler.py    # Multi-format text extraction
│   ├── groq_client.py      # Groq AI summarization
│   ├── content_filter.py   # Profanity/safety check
│   ├── output_writer.py    # Multi-format file writer
│   └── tts_engine.py       # gTTS voice reading
├── tests/                  # pytest test suite
├── docs/flowchart.md       # Mermaid diagram
└── output_files/           # Generated digests
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Free key from console.groq.com |

---

## License

MIT © 2025
# Capstone_text_digest
