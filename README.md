# TG Notes Toolkit

This project provides services for importing, processing, and generating exercises from multilingual notes. The implementation
relies only on the Python standard library but exposes hooks for advanced dependencies such as `pdfplumber` or `pytesseract`
when available.

## Features

- SQLite-backed storage for notes and generated exercises including metadata.
- Importers for PDF documents, raw text, web content (including Notion pages via token headers), and OCR-ready images.
- Text processing pipeline covering cleaning, lightweight language detection, tokenisation, and lexical extraction.
- Exercise generator producing structured `move_words` and `recall_words` protocols suitable for downstream consumption.
- Comprehensive unit and integration tests demonstrating PDF, web, and OCR ingestion flows.

## Tests

Run the automated test-suite with:

```bash
pytest
```
