# Room 5: Background Batch Worker (`worker/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`worker` encapsulates scheduled batch processing, historical replay pipelines, daily soiling tracking routines, and operational forecast generation jobs.

### Locked Architectural Invariants
- **Out-of-Band Execution**: Worker jobs run decoupled from the FastAPI request/response lifecycle, interacting with the database via idempotent batch inserts and upserts.
- **Explicit Reference Dates**: All worker routines accept explicit `target_date: date` or `as_of_date: date` parameters. Zero usage of local machine time (`datetime.now()`).
- **Soiling-Adjusted Forecast (Engineering Decision #6)**: In `forecast_job`, model power predictions MUST be scaled by the prevailing soiling derating:
  $$P_{\text{final\_forecast}} = P_{\text{model}} \times \left(1.0 - \frac{\text{soiling\_loss\_pct}}{100.0}\right)$$
- **Physical Guardrail Enforcement**: Every batch prediction produced by `forecast_job` must be processed through `solar_core.validator.apply_guardrails` (H1-H5) before being committed to `model_forecast`.

---

## 2. Job Catalog (`worker/jobs.py`)

### `replay_job(target_date: date, plant_id: str = "dka_01")`
- Simulates real-time plant telemetry streaming by reading a single historical day from processed telemetry and writing records to the `measurements` table.
- Enables demonstration and regression testing without physical hardware connectivity.

### `soiling_job(target_date: date, plant_id: str = "dka_01")`
- Evaluates the preceding day's hourly telemetry through `solar_core.soiling.compute_daily_pr_tc`.
- Computes temperature-corrected performance ratio ($\text{PR}_{\text{tc}}$), updates 14-day rolling median ($\text{PR}_{\text{smooth}}$), and evaluates soiling rate (%/day).
- Persists results to `plant_health_daily` and raises alerts in `alerts` if soiling loss exceeds thresholds.

### `forecast_job(as_of_date: date, plant_id: str = "dka_01")`
- Loads active model from `models/ACTIVE/model.json` and `metadata.json`.
- Fetches day-ahead weather forecasts from `weather_forecast`.
- Evaluates clear-sky reference power via `solar_core.physics`.
- Computes predicted power, applies hard guardrails (H1-H5), derates for soiling loss (Decision #6), and populates `model_forecast`.

---

## 3. Current Implementation Status

- **`jobs.py`**:
  - `replay_job`, `soiling_job`, and `forecast_job` are fully defined with type-annotated function signatures and docstrings.
  - Currently raising `NotImplementedError` as walking-skeleton contract stubs, scheduled for Sprint 2 implementation.
