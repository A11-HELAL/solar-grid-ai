# Room 6: Analytical API Service (`api/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`api` provides the read-only RESTful analytical backend for Solar-Grid AI, serving telemetry, model forecasts, plant health analytics, alerts, and model guardrail monitoring to the UI and external grid operators.

### Locked Architectural Invariants
- **OpenAPI 3.0 Contract Adherence**: All route paths, parameters, request bodies, and response payloads MUST strictly match `docs/openapi.json` (verified by `tests/test_contract.py`).
- **Deterministic Mock Mode (`MOCK=1`)**: When `MOCK=1` environment variable is set, the API service must return pre-baked deterministic JSON fixtures without requiring an active PostgreSQL database.
- **Demo Reference Clock (Engineering Decision #7)**: Since historical datasets do not extend to the current calendar day, time queries MUST compute reference time as $\tau_{\text{ref}} = \max(\text{ts\_utc})$ from the `measurements` table instead of calling host system `NOW()` or `CURRENT_DATE`.
- **Read-Only Separation**: The API serves analytical queries; long-running model training and bulk data ingest are strictly isolated to `ml_training/` and `worker/`.

---

## 2. Analytical Endpoints Roster (8 Operations in `docs/openapi.json`)

| Method | Endpoint | Purpose | Key Parameters / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Health & DB connectivity probe | Returns `{ "status": "ok", "version": "1.1.0" }` |
| `GET` | `/api/v1/plants` | Plant metadata & nameplate configuration | Returns list of configured plants (`dka_01`) |
| `GET` | `/api/v1/plants/{id}/forecast` | 24-48h day-ahead forecast with guardrails | `start_date`, `end_date`, `model_version` |
| `GET` | `/api/v1/plants/{id}/measurements` | Historical telemetry time series | `start_date`, `end_date`, `limit` |
| `POST` | `/api/v1/plants/{id}/measurements` | Telemetry batch ingestion endpoint | Batch array of timestamped measurement records |
| `GET` | `/api/v1/plants/{id}/health` | Daily temperature-corrected PR & soiling | `start_date`, `end_date` |
| `GET` | `/api/v1/plants/{id}/alerts` | Active and historical operational alerts | `severity`, `acknowledged` |
| `GET` | `/api/v1/plants/{id}/model-health` | Guardrail hit rate, fallback rates, drift | `window_days`, `model_version` |

---

## 3. Current Implementation Status

- **`main.py`**:
  - FastAPI application initialized with metadata (v1.1.0).
  - `GET /api/v1/health` fully implemented and responding.
  - Contract validation in `tests/test_contract.py` actively passes against `docs/openapi.json`.
  - Remaining 7 endpoint routes are walking-skeleton stubs scheduled for Sprint 2 completion.
