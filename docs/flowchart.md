# Capstone_text_digest — Program Flowchart

This file contains the Mermaid diagram source for the application flow.
GitHub renders Mermaid diagrams natively in Markdown files.

```mermaid
flowchart TD
    A([🚀 Launch Streamlit App]) --> B[User selects input mode:\nUpload File or Enter URL]

    B --> C{Input type?}

    C -->|.txt file| D[extract_from_txt\nRead UTF-8 bytes]
    C -->|.pdf file| E[extract_from_pdf\nPyMuPDF page join]
    C -->|.doc/.docx| F[extract_from_docx\npython-docx paragraphs]
    C -->|.rtf file| G[extract_from_rtf\nstriprtf → plain text]
    C -->|HTTP URL| H[extract_from_url\nrequests + BeautifulSoup]

    D & E & F & G & H --> I[detect_title\nFirst non-empty line]

    I --> J[User configures:\n• Output format\n• Style\n• Voice reading toggle]

    J --> K[build_prompt\nGroq LLaMA-3.1-8B instruction]

    K --> L[Groq API call\nllama-3.1-8b-instant free]

    L --> M{Content filter\nbetter-profanity check}

    M -->|❌ Contains\ninappropriate language| N[sanitize text\ncensor flagged words]
    N --> O[⚠️ Warn user in UI]
    O --> P[Use sanitized digest]

    M -->|✅ Clean| P

    P --> Q[Add 2-line header\nLine 1: Original Title\nLine 2: Style Descriptor]

    Q --> R{Output format?}

    R -->|txt| S1[write_txt\nplain UTF-8 file]
    R -->|pdf| S2[write_pdf\nfpdf2 document]
    R -->|docx| S3[write_docx\npython-docx document]
    R -->|rtf| S4[write_rtf\nRTF 1.5 string]
    R -->|html| S5[write_html\nHTML page with CSS]

    S1 & S2 & S3 & S4 & S5 --> T[📥 Download button\nin Streamlit UI]

    T --> U{Voice reading\nrequested?}

    U -->|Yes| V[gTTS text_to_speech\nGenerate MP3 bytes]
    V --> W[🔊 st.audio player\n+ MP3 download button]
    W --> X([✅ Complete])

    U -->|No| X

    style A fill:#4CAF50,color:#fff
    style X fill:#4CAF50,color:#fff
    style N fill:#FF9800,color:#fff
    style O fill:#FF9800,color:#fff
    style L fill:#2196F3,color:#fff
    style V fill:#9C27B0,color:#fff
```

## Data Flow Summary

| Stage | Module | Input | Output |
|---|---|---|---|
| 1. Extract | `input_handler.py` | File / URL | `(title, body)` strings |
| 2. Summarize | `groq_client.py` | title, body, style, api_key | Digest string |
| 3. Filter | `content_filter.py` | Digest string | `(bool, safe_string)` |
| 4. Write | `output_writer.py` | header1, header2, body, format | File path |
| 5. Read aloud | `tts_engine.py` | Full text string | MP3 bytes |
| 6. Display | `app.py` | All of the above | Streamlit UI elements |
