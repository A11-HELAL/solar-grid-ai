# Room 1: Data Pipeline (`data_pipeline/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`data_pipeline` owns offline batch ingestion, cleaning, timezone normalization, hourly resampling, quality flag tagging, and dataset staging for Solar-Grid AI.

### Locked Architectural Invariants
- **Fractional Timezone Resampling (Engineering Decision #4)**: Raw telemetry from Alice Springs is stamped in `Australia/Darwin` (`UTC+09:30`). The pipeline MUST subtract 9 hours and 30 minutes (`-9.5h`) FIRST to convert to true UTC, and THEN apply `.resample('1h', closed='right', label='right')`. Resampling before timezone shifting produces erroneous solar peak hours.
- **Strict Ban on `fillna(0)` (Constitution Principle IV)**: Imputing missing daytime telemetry with zero is strictly forbidden; it artificially depresses capacity factors and biases ML loss functions.
- **The 5 Canonical Quality Flags**:
  1. `ok`: Clean, physically verified measurement.
  2. `interpolated`: Missing data spanning $\le 2$ consecutive hours, linearly interpolated.
  3. `missing`: Gap $> 2$ hours. Left as NaN with flag `missing`; NEVER interpolated.
  4. `fault_suspect`: Daytime high irradiance ($G_{\text{poa}} > 200\text{ W/m}^2$) with frozen or near-zero power ($< 0.05\text{ kW}$). Excluded from training sets; preserved for anomaly detection benchmarks.
  5. `night`: Solar zenith $> 90^\circ$ or clear-sky power $< 0.1\text{ kW}$. Power clamped strictly to $0.0\text{ kW}$.
- **Raw DKASC Invariants**:
  - Target CSV SHA-256: `eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0`.
  - Corrupted Record: Skip corrupted line 1,767,915 (contains 23 fields instead of 14).
  - Sensor Handling: Drop 100% NaN `Wind_Speed` column and corrupted raw `Performance_Ratio`. Impute `wind_speed_ms` from Open-Meteo `wind_speed_10m`.

---

## 2. Module Roster & Current Implementation Status

### `ingest.py` (Current Status: PARTIALLY IMPLEMENTED - 6 Passing Tests)
- **`ingest_open_meteo(csv_path)`** *(IMPLEMENTED)*:
  - Loads hourly weather dataset (`data/raw/open_meteo_dka_2023_2025.csv`).
  - Validates exact schema: `ts_utc`, `ghi_wm2`, `dni_wm2`, `dhi_wm2`, `temp_ambient_c`, `wind_speed_ms`, `cloud_cover_pct`.
  - Validates UTC timezone parsing and enforces zero NaN values.
  - Verified by 6 unit tests in `tests/test_weather_ingest.py`.
- **`ingest_raw_dka(csv_path)`** *(SKELETON CONTRACT - Sprint 1)*:
  - Streaming chunked parser for multi-gigabyte raw DKASC 5-minute CSV.
  - Handles line skips, column renaming, and initial range checks.

### `clean.py` (Current Status: SKELETON CONTRACT - Sprint 1)
- **`clean_and_resample_hourly(raw_df)`**:
  - Executes `-9.5h` shift to convert Darwin timestamps to UTC.
  - Applies `resample('1h', closed='right', label='right')`.
  - Tags every record with one of the 5 canonical quality flags.
  - Computes Faiman module temperature ($T_{\text{cell}}$) using `solar_core.physics`.
  - Exports clean parquet and CSV files to `data/processed/`.
