# Solar-Grid AI v1.1 - Architectural Context & Guidance Manual

Physics-Guided Solar Energy Forecasting & Grid Intelligence for DKASC Site 14 (`dka_01`).

---

## 1. Architectural Architecture: The 8 Decoupled Rooms

The repository is structured as an **8-Room Decoupled Monolith**. The use of a generic `src/` directory is strictly forbidden (enforced by `tests/test_layout.py`).

| Room | Directory | Architectural Responsibility | Current Status |
| :--- | :--- | :--- | :--- |
| **Room 1** | `data_pipeline/` | Offline ETL: DKA Site 14 & Open-Meteo ingestion, timezone shift (`-9.5h`), hourly resampling, quality flag tagging. | `ingest.py` implemented (6 passing tests); `clean.py` walking-skeleton stub. |
| **Room 2** | `packages/solar_core/` | 100% pure deterministic physics domain engine (solar geometry, clear-sky power, guardrails H1-H5, soiling, simulation). Zero DB/HTTP/clock dependencies. | `config.py` implemented (15 passing tests); other modules walking-skeleton stubs. |
| **Room 3** | `ml_training/` | Offline ML training harness, chronological 70/15/15 split, model zoo (M0-M4 clear-sky ratio XGBoost), native JSON export (`model.json`), MR1-MR8 validation. | Walking-skeleton contract stubs (Sprint 2). |
| **Room 4** | `db/` | PostgreSQL 16 relational schema (`01_schema.sql`), time-series indexing, idempotency fixtures. | Schema locked (`db/init/01_schema.sql`). |
| **Room 5** | `worker/` | Scheduled out-of-band operational jobs (`replay_job`, `soiling_job`, `forecast_job`). | Walking-skeleton contract stubs (Sprint 2). |
| **Room 6** | `api/` | Read-only FastAPI service exposing 8 analytical endpoints (`docs/openapi.json`), `MOCK=1` fixture mode. | Health endpoint active; verified against OpenAPI contract (1 passing test). |
| **Room 7** | `ui/` | React 18 + Vite + Recharts analytical dashboard (3 views: Overview, Forecast & Health, Anomaly Deep Dive). | Scaffolded walking skeleton (Sprint 2). |
| **Room 8** | `tests/` | Test suite: monorepo layout, OpenAPI contract validation, immutable config validation, weather ingest, metamorphic QA gate (MR1-MR8). | 25 passing tests active. |

### Operational Directories
- `data/raw/`: Raw telemetry files (DKASC 5-min CSV, Open-Meteo hourly weather CSV).
- `data/processed/`: Cleaned, resampled hourly parquet/CSV datasets with quality flags.
- `models/ACTIVE/`: Currently deployed model artifacts (`model.json` + `metadata.json`).

---

## 2. Authoritative Plant Constants (DKASC Site 14 / `dka_01`)

Codified in `plant_config.yaml` and loaded via `solar_core.config.load_plant_config`:

- **Plant Identifier**: `dka_01` (DKA Solar Centre Site 14, Alice Springs, Northern Territory, Australia)
- **Geographic Coordinates**: Latitude `-23.7618°`, Longitude `133.8748°`, Elevation `545.0 m`
- **Native Timezone**: `Australia/Darwin` (`UTC+09:30` -> converted to UTC via explicit `-9.5h` shift)
- **Array Nameplate Rating**: `5.4 kWp` DC (Mono-Si array)
- **Inverter AC Ceiling**: `5.0 kW` AC (Strict physical clipping cap)
- **Geometry**: Tilt `20.0°` (fixed latitude tilt), Azimuth `0.0°` (True North)
- **Physics Constants**:
  - Cell Temperature Coefficient: `γ = -0.004 / °C` (-0.4%/°C drop above 25°C)
  - Reference Temperature: `T_ref = 25.0 °C`
  - Empirical Calibration Factor: `0.92` (clearest training days empirical correction)
  - Nighttime Threshold: `0.1 kW` (values below 0.1 kW or zenith > 90° clamped to 0.0 kW)

---

## 3. Current Implementation Status (Sprint 1)

The monorepo currently contains a fully established foundational walking skeleton with **25 passing tests** in `pytest`:
1. `packages/solar_core/config.py`: Complete immutable `PlantConfig` dataclass (`frozen=True`) and physical boundary validation in `load_plant_config` (15 unit tests passing).
2. `data_pipeline/ingest.py`: Complete `ingest_open_meteo` parser validating column schemas, UTC timestamps, and zero-NaN integrity against `data/raw/open_meteo_dka_2023_2025.csv` (6 unit tests passing).
3. `tests/test_layout.py`: Monorepo structure verification ensuring 8 rooms and operational directories exist and no `src/` exists (3 tests passing).
4. `tests/test_contract.py`: OpenAPI 3.0 schema contract verification validating all 8 analytical endpoints in `docs/openapi.json` (1 test passing).
5. Other modules (`physics.py`, `clean.py`, `train.py`, `worker/jobs.py`, `api/main.py`) are strictly typed walking-skeleton contract stubs raising `NotImplementedError`, scheduled for Sprint 1-2 implementation.

---

## 4. Locked Cross-Room Architectural Contracts & Invariants

1. **100% Pure Core (`packages/solar_core/`)**: Zero database drivers, zero HTTP clients, zero system clock queries (`datetime.now()` forbidden), and zero pickle. Deterministic mathematical functions only.
2. **Timezone Handling**: Telemetry from Alice Springs (`UTC+09:30`) must be shifted by `-9.5h` to UTC prior to `resample('1h', closed='right', label='right')`.
3. **Strict Ban on `fillna(0)`**: Zero-filling missing telemetry is strictly prohibited to prevent artificial capacity factor depression. 5 canonical quality flags must be used: `ok`, `interpolated`, `missing`, `fault_suspect`, `night`.
4. **Ratio Modeling with Monotone Constraints**: ML models predict clear-sky ratio $r = \text{clip}(P_{\text{actual}} / P_{\text{clear\_sky}}, 0.0, 1.1)$ with sample weights proportional to $P_{\text{clear\_sky}}$ and monotone gradient constraints (+1 irradiance, -1 cloud cover, -1 temperature).
5. **No Pickle Serialization**: All models must be exported exclusively as portable `model.json` (weights/trees) and `metadata.json` (hyperparameters, git hash, metrics).
6. **Hard Guardrails (H1-H5)**: Every inference output must pass finite check (H1), night zeroing (H2), negative clipping (H3), clear-sky 1.1 ceiling cap (H4), and inverter 5.0 kW capacity cap (H5).
7. **Metamorphic QA Gate (MR1-MR8)**: All models must achieve ≥ 95% pass rate across the 8 metamorphic relations before promotion to `models/ACTIVE/`.
8. **Demo Reference Clock**: All database and API queries must reference `MAX(ts_utc)` from the `measurements` table instead of host `NOW()`.
