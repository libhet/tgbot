# Architecture Overview

This document summarises the key components underpinning the Telegram learning bot infrastructure defined in this repository.

## High-Level Components

1. **API Layer (FastAPI, optional)**
   - Hosts REST endpoints for authentication, localization, and health checks.
   - Instruments metrics through Prometheus middleware when available.
   - Provides structured logging for operational insights.

2. **Persistence Layer (SQLite runtime)**
   - Stores user identities, Telegram IDs, and linked third-party accounts using the standard library `sqlite3` module.
   - Offers asynchronous-style helpers (`asyncio.to_thread`) for compatibility with async code.
   - Ready to be replaced with a remote PostgreSQL instance when running inside Docker.

3. **Localization**
   - Runtime translation catalog living in `app/localization/translator.py`.
   - Configurable default and supported locales via environment variables.
   - Extensible with new languages by updating translation dictionaries.

4. **Observability**
   - Prometheus can scrape `/metrics` from the API container when instrumentation extras are installed.
   - Grafana visualises metrics and supports alerting rules (see `docker-compose.yml`).
   - Optional Sentry DSN configuration for error tracking.

5. **Security & Access Control**
   - Authorization ensures only whitelisted Telegram IDs can access privileged functionality.
   - Secrets managed through environment variables to avoid source control exposure.

6. **Backups**
   - `scripts/backup_database.sh` orchestrates `pg_dump` for PostgreSQL deployments.
   - Integrate with cron or CI jobs for automated scheduled backups.

## Deployment Workflow

1. Developers push changes to GitHub.
2. GitHub Actions executes linting and tests (`.github/workflows/ci.yml`).
3. Successful runs can trigger deployment pipelines (configure additional jobs as required).
4. Docker image can be built from `Dockerfile` and deployed to the target platform (e.g. Heroku container registry).

## Telegram Authentication Flow

1. Frontend/mini-app obtains the signed Telegram user payload.
2. Payload is forwarded to `/auth/telegram`.
3. Service creates or updates user records and verifies access control against the configured whitelist.
4. API responds with localized confirmation message and user metadata.

## Extending the System

- **Additional Services:** Create new modules for OCR processing, exercise scheduling, etc.
- **Localization:** Expand translation dictionaries and update UI components accordingly.
- **Monitoring:** Add Grafana dashboards and alert rules stored under `monitoring/`.
- **CI/CD:** Append deployment stages to the GitHub Actions workflow (e.g. container release to production).

## Data Model Diagram

```
User (1) --- (N) Account
```

- `User`: Telegram identity and profile metadata.
- `Account`: External service integrations linked to a user.

## Backup & Disaster Recovery

- Store generated SQL dumps in a secure bucket (S3, GCS).
- Automate `scripts/backup_database.sh` via cronjob or GitHub Actions scheduled workflow.
- Document restoration procedures in runbooks.

## Future Enhancements

- Integrate OAuth providers for third-party account linking.
- Replace simple translation dictionary with gettext or LinguiJS for advanced localization.
- Add role-based access control and admin dashboards.
- Introduce tracing (OpenTelemetry) for distributed diagnostics.
