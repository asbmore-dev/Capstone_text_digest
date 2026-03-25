"""
input_handler.py
Parses all supported input sources and returns a (title, body) tuple.

Supported sources:
  - Streamlit UploadedFile: .txt, .pdf, .doc, .docx, .rtf
  - URL string: any HTTP/HTTPS page
"""

from __future__ import annotations

import io
import re


# ── Title detection ───────────────────────────────────────────────────────────

def detect_title(text: str) -> str:
    """Return the first non-empty line as the document title."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            # Truncate very long first lines
            return stripped[:120]
    return "Untitled Document"


# ── Format extractors ─────────────────────────────────────────────────────────

def extract_from_txt(file) -> tuple[str, str]:
    """Read a plain UTF-8 text file."""
    raw = file.read()
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="ignore")
    else:
        text = raw
    text = text.strip()
    return detect_title(text), text


def extract_from_pdf(file) -> tuple[str, str]:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("Install PyMuPDF: uv add pymupdf")

    raw = file.read() if hasattr(file, "read") else file
    doc = fitz.open(stream=raw, filetype="pdf")

    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()

    text = "\n\n".join(pages).strip()
    if not text:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It may be a scanned image — OCR is not supported in this version."
        )
    return detect_title(text), text


def extract_from_docx(file) -> tuple[str, str]:
    """Extract text from a .docx file using python-docx."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("Install python-docx: uv add python-docx")

    raw = file.read() if hasattr(file, "read") else file
    doc = Document(io.BytesIO(raw))

    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n\n".join(paragraphs).strip()

    if not text:
        raise ValueError("No text could be extracted from this DOCX file.")
    return detect_title(text), text


def extract_from_rtf(file) -> tuple[str, str]:
    """Strip RTF markup and return plain text."""
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError:
        raise ImportError("Install striprtf: uv add striprtf")

    raw = file.read() if hasattr(file, "read") else file
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="ignore")

    text = rtf_to_text(raw).strip()
    if not text:
        raise ValueError("No text could be extracted from this RTF file.")
    return detect_title(text), text


def extract_from_url(url: str) -> tuple[str, str]:
    """Scrape text content from an HTTP/HTTPS URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("Install requests and beautifulsoup4: uv add requests beautifulsoup4")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError(f"Request timed out for URL: {url}")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to: {url}")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error {e.response.status_code} for URL: {url}")

    soup = BeautifulSoup(response.text, "lxml")

    # Remove boilerplate tags
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "noscript", "iframe"]):
        tag.decompose()

    # Try to find the page title
    title = ""
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)

    # Extract paragraph text
    paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) > 40]  # drop nav fragments

    body = "\n\n".join(paragraphs).strip()

    if not body:
        # Fallback: grab all visible text
        body = soup.get_text(separator="\n", strip=True)

    if not body:
        raise ValueError(f"No readable text content found at: {url}")

    if not title:
        title = detect_title(body)

    return title[:120], body


# ── Public router ─────────────────────────────────────────────────────────────

def parse_input(source) -> tuple[str, str]:
    """
    Route to the correct extractor based on source type.

    Args:
        source: A Streamlit UploadedFile object OR a URL string.

    Returns:
        (title, body) tuple — both plain strings.

    Raises:
        ValueError: If the format is unsupported or extraction fails.
    """
    # URL string
    if isinstance(source, str):
        url = source.strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return extract_from_url(url)

    # Streamlit UploadedFile — dispatch on file extension
    name = getattr(source, "name", "").lower()

    if name.endswith(".txt"):
        return extract_from_txt(source)
    elif name.endswith(".pdf"):
        return extract_from_pdf(source)
    elif name.endswith((".docx", ".doc")):
        return extract_from_docx(source)
    elif name.endswith(".rtf"):
        return extract_from_rtf(source)
    else:
        # Fallback: try plain text
        try:
            return extract_from_txt(source)
        except Exception:
            raise ValueError(
                f"Unsupported file type: '{name}'. "
                "Supported formats: .txt, .pdf, .doc, .docx, .rtf"
            )
