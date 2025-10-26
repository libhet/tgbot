# Telegram Learning Bot Infrastructure

This repository provides an infrastructure scaffold for a Telegram learning bot. It focuses on environment configuration, authentication, localization, observability, backups, and documentation to streamline collaboration.

## Features

- **Container-ready environment** via `docker-compose` with optional PostgreSQL, Prometheus, and Grafana services.
- **CI/CD pipeline** using GitHub Actions for linting and automated testing.
- **Environment-based configuration** for sensitive secrets (Telegram bot token, OCR keys, etc.).
- **User authentication service** leveraging a lightweight SQLite persistence layer by default.
- **Localization** helper supporting English and Russian with easy extension for additional locales.
- **Monitoring and logging** hooks (Prometheus metrics endpoint, structured logging configuration).
- **Backup tooling** for database snapshots.

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended for full stack)
- Python 3.11 (optional for running locally without Docker)
- `pg_dump` utility for PostgreSQL backups (optional)

### Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token retrieved from BotFather. |
| `DATABASE_URL` | Database URL (SQLite by default, e.g. `sqlite:///app.db`). |
| `DEFAULT_LOCALE` | Default locale identifier (e.g. `en`). |
| `SUPPORTED_LOCALES` | Comma separated list of supported locales. |
| `ALLOWED_TELEGRAM_USER_IDS` | Optional comma separated list of privileged user IDs. |
| `OCR_API_KEY` | API key for OCR provider (optional). |
| `OCR_ENDPOINT` | OCR provider endpoint URL (optional). |
| `SENTRY_DSN` | Sentry DSN for error tracking (optional). |

### Running with Docker

```bash
docker compose up --build
```

The API becomes available at <http://localhost:8000> once optional FastAPI dependencies are installed inside the container.

### Local Development (without Docker)

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install optional runtime dependencies for the HTTP API:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the service:
   ```bash
   python -m app.main
   ```

> **Note:** The core modules (configuration, authentication services, localization, backup utilities) do not depend on external libraries and can be reused in other contexts. FastAPI/Uvicorn/Prometheus are optional extras for running the HTTP API.

### Running Tests
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

## API Overview

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check returning localized message. |
| `GET` | `/locales` | List supported locales. |
| `POST` | `/auth/telegram` | Register or authenticate Telegram users. |

Swagger UI is available at `/docs` once FastAPI dependencies are installed and the server is running.

### Authentication Flow

1. Telegram mini-app sends a `POST /auth/telegram` request with the signed user payload provided by Telegram.
2. The service stores or updates the user record (using SQLite by default).
3. If `ALLOWED_TELEGRAM_USER_IDS` is set, the service validates access.
4. Response includes internal user ID, Telegram ID, locale, and localized success message.

## Localization

Localized strings live in `app/localization/translator.py`. Add new keys and languages by extending the `TRANSLATIONS` dictionary and updating `SUPPORTED_LOCALES` in configuration.

## Monitoring & Logging

- Logs follow a structured format configured in `app/logging_config.py`.
- Prometheus metrics can be exposed at `/metrics` via the optional `prometheus-fastapi-instrumentator` package.
- Grafana dashboards can visualise metrics collected by Prometheus (see `docker-compose.yml`).

## Backups

Run scheduled backups using the helper script:

```bash
./scripts/backup_database.sh
```

Ensure `pg_dump` is available and `DATABASE_URL` points to a PostgreSQL instance when using the script.

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) installs optional development dependencies, runs linting (Black/Isort), and executes Pytest. Customize the workflow to add deployment steps (e.g., to Heroku) as required.

## Deployment Notes

- Provide environment variables via your deployment platform.
- Docker image (`Dockerfile`) includes the optional FastAPI stack; ensure dependencies are installed before running the service.
- Configure alerts within Grafana or integrate with Sentry for proactive monitoring.

## Architecture Documentation

Additional architectural decisions and process flows are documented in [`docs/architecture.md`](docs/architecture.md).
