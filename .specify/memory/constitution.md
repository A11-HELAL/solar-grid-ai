<!--
# Sync Impact Report
- Version change: 1.1.0 -> 1.2.0
- List of modified principles:
  - I. Strict Sequential Execution & Resource Governance -> I. Decoupled Monolith Architecture (The 8 Rooms)
  - II. Canonical Monorepo & Pure Functional Core -> II. Pure Physics Engine (packages/solar_core/)
  - III. Mandatory Physics & Data Audit Decisions -> III. Canonical Plant Configuration & Empirical Truths (plant_config.yaml)
  - IV. Metamorphic Testing & Strict Physics QA Gates -> IV. Data Quality, Timezone Standards & Missing Sensor Governance
  - V. Tiered Delegation & Multi-Guard Verification -> V. ML Clear-Sky Modeling, Portable Serialization & Strict Validation (H1-H5, MR1-MR8)
- Added sections:
  - VI. Clean Code, Resource Governance & Rigorous Testing (New Principle VI)
  - The 8 Architectural Rooms & System Contracts (Expanded architectural specifications)
- Removed sections: None (operational constraints and delegation rules consolidated into Principle VI and Workflow Gates)
- Follow-up TODOs: None (all template placeholders fully resolved)
-->

# Solar-Grid AI (v1.1) Constitution

## Core Principles

### I. Decoupled Monolith Architecture (The 8 Rooms)
All codebase artifacts and implementation routines MUST strictly reside within the 8 canonical architectural rooms. The use of a generic `src/` directory is STRICTLY FORBIDDEN. The 8 rooms and their strict operational responsibilities are:
1. `data_pipeline/` (Room 1): Ingestion, cleaning, fractional timezone shifting, hourly aggregation, quality flag tagging, synthetic anomaly injection, and sample generation.
2. `packages/solar_core/` (Room 2): Pure physics and solar domain engine (solar position, clear-sky irradiance, thermal cell temperature, physical validators, soiling derating, and synthetic PV simulation).
3. `ml_training/` (Room 3): Feature engineering pipelines, model zoo (M0 Baseline through M4 Clear-Sky Ratio XGBoost), training harnesses, and hyperparameter tuning.
4. `db/` (Room 4): Relational database schemas (`01_schema.sql`), seed fixtures, migrations, and idempotent database initialization scripts.
5. `worker/` (Room 5): Background task execution and scheduled operational jobs (`replay_job`, `soiling_job`, `forecast_job`).
6. `api/` (Room 6): FastAPI analytical backend service exposing 8 read-only analytical JSON endpoints.
7. `ui/` (Room 7): Frontend dashboard built with React, Vite, and Recharts providing 3 synchronized operational views (Plant Overview, Forecast & Health, Anomaly Deep Dive).
8. `tests/` (Room 8): Comprehensive testing suite housing the Metamorphic QA Gate (MR1–MR8), room-level unit tests, contract verification, and CI test pipelines.

Circular dependencies across rooms are prohibited. Upstream engine rooms (`packages/solar_core/`) MUST remain fully agnostic of downstream persistence, worker runtimes, API frameworks, and user interfaces.
*Rationale*: Eliminating generic source folders and enforcing the 8-room decoupled monolith guarantees modular boundaries, simplifies isolation testing, prevents hidden cyclic couplings, and keeps domain logic decoupled from runtime frameworks.

### II. Pure Physics Engine (packages/solar_core/)
All modules within `packages/solar_core/` MUST be implemented as 100% pure functions. Pure physics functions MUST satisfy the following non-negotiable constraints:
- Strictly NO database calls or driver imports (no PostgreSQL, SQLAlchemy, psycopg, or asyncpg).
- Strictly NO network or HTTP requests (no `requests`, `httpx`, `aiohttp`, or `urllib`).
- Strictly NO system clock or local environment queries (`datetime.now()`, `datetime.utcnow()`, and `time.time()` are FORBIDDEN; all timestamps, horizons, and temporal coordinates MUST be passed explicitly as function arguments).
- Strictly NO Python `pickle` serialization.
- Modules within `packages/solar_core/` MUST follow a strict linear internal dependency order: `config.py` -> `physics.py` -> `features.py` & `validator.py` -> `soiling.py` -> `sim.py`.
*Rationale*: System clock queries and external I/O within core domain functions produce Training-Serving Skew, irreproducible calculations, and slow unit test suites. Pure functions guarantee mathematical determinism, instant unit testing, and seamless execution across training and real-time inference.

### III. Canonical Plant Configuration & Empirical Truths (plant_config.yaml)
All physical computations, solar geometries, array deratings, and baseline thresholds MUST be read directly from `plant_config.yaml` based on the audited empirical truths of DKASC Site 14 (`dka_01`):
- **Plant Identifier**: `dka_01` (DKA Solar Centre Site 14, Alice Springs, Northern Territory, Australia).
- **Array Nameplate Capacity**: `5.4` kWp DC.
- **Inverter Capacity Ceiling**: `5.0` kW AC rated maximum (observed operational peak: `5.018` kW).
- **Array Orientation & Tilt**: Tilt = `20.0` degrees North, Azimuth = `0.0` degrees (due North, Southern Hemisphere convention).
- **Geographic Coordinates**: Latitude `-23.7618`, Longitude `133.8748`, Elevation `545.0` meters.
- **Temperature Coefficient ($\gamma$)**: `-0.004` / °C (-0.40% per °C relative to $T_{\text{ref}} = 25.0$ °C).
- **Calibration Factor**: `0.92` (derived exclusively on the clearest historical training days to capture module degradation and optical attenuation).
- **Nighttime Threshold**: `0.1` kW (`is_night = True` whenever `clear_sky_kw < 0.1` kW or solar zenith angle $\theta_z > 90.0^\circ$).
Hardcoding magic numbers in physics or feature extraction modules is strictly forbidden; all routines MUST accept configuration objects derived from `plant_config.yaml`.
*Rationale*: A single source of truth for plant physics ensures physical fidelity across all 8 rooms and prevents discrepancy between ingestion filters, model training, and worker inference.

### IV. Data Quality, Timezone Standards & Missing Sensor Governance
All data ingestion, cleaning, transformation, and feature extraction routines MUST adhere to strict timezone and sensor data governance:
1. **Timezone Standardization**: All persisted and processed timestamps MUST be in UTC. Raw DKASC Site 14 telemetry recorded in `Australia/Darwin` (UTC+09:30) MUST shift by exactly -9.5 hours to UTC *before* resampling.
2. **Deterministic Resampling**: Downsampling 5-minute telemetry to hourly intervals MUST use `.resample('1h', closed='right', label='right')`.
3. **Missing Value Governance**: Calling `fillna(0)` on missing sensor readings (irradiance, ambient temperature, module temperature, wind speed) is STRICTLY FORBIDDEN. Zero-filling missing weather observations injects false physical anomalies into feature spaces.
4. **Sensor Imputation & Derived Metrics**:
   - The 100% NaN DKA `Wind_Speed` column and corrupted `Performance_Ratio` column MUST be dropped during ingestion.
   - Wind speed MUST be imputed from Open-Meteo `wind_speed_10m` telemetry.
   - Module temperature MUST be derived using `pvlib.temperature.faiman(poa_wm2, temp_air_c, wind_ms)`.
5. **Quality Flag Classification**: All telemetry records MUST be classified into one of 5 canonical quality flags:
   - `ok`: Validated sensor readings within nominal physical limits.
   - `interpolated`: Continuous missing gaps $\le 2$ hours filled via linear interpolation.
   - `missing`: Continuous gaps $> 2$ hours; interpolation is forbidden, values MUST remain NaN.
   - `fault_suspect`: Daytime periods of high irradiance accompanied by zero or frozen power output; excluded from ML training sets, retained exclusively for fault detection benchmarks.
   - `out_of_range`: Values exceeding physical bounds ($< 0$ or $> 1.2 \times \text{capacity}$).
*Rationale*: Solar data is susceptible to sensor dropouts, fractional timezone distortions, and clipping non-linearities. Strict timezone handling and forbidden `fillna(0)` prevent silent model corruption.

### V. ML Clear-Sky Modeling, Portable Serialization & Strict Validation (H1–H5, MR1–MR8)
Machine learning pipelines in `ml_training/` and serving routines in `worker/` and `packages/solar_core/` MUST adhere to physics-guided modeling, secure serialization, and dual-layer validation gates:
1. **Clear-Sky Ratio Modeling**: ML models MUST predict the bounded clear-sky ratio rather than raw power:
   $$r = \text{clip}\left(\frac{P_{\text{actual}}}{\text{clear\_sky\_kw}}, 0.0, 1.1\right)$$
   Inference power is reconstructed as $P_{\text{pred}} = \hat{r} \times P_{\text{clear\_sky}}$. During XGBoost training, `sample_weight = clear_sky_kw` MUST be supplied to eliminate nighttime bias, and monotone constraints (+1 irradiance, -1 cloud cover, -1 temperature) MUST be enforced.
2. **Portable Model Serialization**: Exporting models using Python `pickle` (`.pkl`) is STRICTLY FORBIDDEN. Trained models MUST be saved and loaded exclusively as portable JSON artifacts: `model.json` (weights and tree definitions) and `metadata.json` (feature names, ordering, hyperparameters, training git commit hash, and validation metrics).
3. **Hard Guardrails (H1–H5)**: Every model prediction emitted by `validator.py` MUST strictly pass through the 5 hard guardrails:
   - **H1 (Finite Output)**: If predicted value is NaN or Inf, trigger fallback (`fallback_used = True`, `rule_hit = 'H1_NAN_OR_INF'`).
   - **H2 (Night Zeroing)**: If `is_night == True` and raw prediction $> 0.0$, clamp `final_kw = 0.0` (`guardrail_activated = True`, `rule_hit = 'H2_NIGHT_ZERO'`).
   - **H3 (Non-Negativity)**: If raw prediction $< 0.0$, clamp `final_kw = 0.0` (`guardrail_activated = True`, `rule_hit = 'H3_NEGATIVE_CLIP'`).
   - **H4 (Clear-Sky Ceiling)**: If raw prediction $> 1.1 \times \text{clear\_sky\_kw}$, clamp `final_kw = 1.1 * clear_sky_kw` (`guardrail_activated = True`, `rule_hit = 'H4_CLEAR_SKY_CAP'`).
   - **H5 (Capacity Ceiling)**: If raw prediction $> \min(\text{inverter\_cap}, \text{capacity\_kwp})$ ($5.0$ kW), clamp `final_kw = min(inverter_cap, final_kw)` (`guardrail_activated = True`, `rule_hit = 'H5_CAPACITY_CAP'`).
   - **Soft Suspicion Alert (S1)**: If $\text{clear\_sky\_kw} \ge 2.0$ kW, $\text{cloud\_cover} < 20\%$, and $\text{final\_kw} < 0.15 \times \text{clear\_sky\_kw}$, flag `rule_hit = 'S1_LOW_CLEAR_DAY_WARN'`.
   - **Model Health Drift Gate**: Guardrail activation rate across evaluation batches $> 5\%$ raises a `WARNING`; activation rate $> 15\%$ triggers a `CRITICAL` alert.
4. **Metamorphic QA Gate (MR1–MR8)**: No model artifact MAY be promoted to `models/ACTIVE` without achieving a $\ge 95\%$ pass rate across the full metamorphic test catalog:
   - **MR1 (Irradiance Monotonicity)**: $+100 \text{ W/m}^2$ POA irradiance under daytime conditions MUST NOT decrease predicted power ($\frac{\partial P}{\partial G} \ge 0$).
   - **MR2 (Thermal Monotonicity)**: Increasing ambient temperature from $25^\circ\text{C}$ to $45^\circ\text{C}$ (+20°C) under high irradiance MUST decrease power with $P_{\text{hot}} / P_{\text{base}} \in [0.85, 0.97]$ (theoretical physics $\approx 0.92$).
   - **MR3 (Cloud Opacity Damping)**: Increasing cloud cover percentage holding geometry fixed MUST NOT increase predicted power.
   - **MR4 (Nighttime Invariance)**: When solar zenith $> 90^\circ$ (`is_night == True`), any weather perturbation MUST still yield $P_{\text{pred}} = 0.0$ kW.
   - **MR5 (Coordinate / Timezone Invariance)**: Telemetry evaluated under Australia/Darwin local time vs UTC representation MUST yield identical predictions.
   - **MR6 (Capacity Proportionality)**: Doubling array capacity in configuration MUST double predicted power under identical weather.
   - **MR7 (Soiling Continuity)**: Multiplying power measurements by $0.9$ MUST yield identical estimated degradation rate (%/day) and state transitions.
   - **MR8 (Dust Accumulation Monotonicity & Bounded Ratio)**: Increasing injected dust rate MUST trigger cleaning alerts on or before the baseline alert date. Reconstructed power MUST NEVER produce negative values or NaN.
*Rationale*: Statistical error metrics (RMSE/MAE) often mask physical absurdities. Metamorphic testing and hard guardrails mathematically guarantee physical consistency across edge cases.

### VI. Clean Code, Resource Governance & Rigorous Testing (clean-code-guard & test-guard)
All contributions across the 8 rooms MUST enforce clean code standards, resource fences, and rigorous testing gates:
1. **Clean Code Guard (`clean-code-guard`)**:
   - Small, focused, single-purpose pure functions.
   - Strict static type hinting on all function signatures, parameters, and return types.
   - Zero AI Fluff: Boilerplate comments, chatty narratives, marketing descriptions, and decorative greetings are strictly forbidden in codebase files. Comments MUST exclusively explain non-obvious mathematical algorithms, physical invariants, or domain assumptions.
2. **Test Guard (`test-guard`)**:
   - 100% pytest pass rate required across all test suites before merge or promotion.
   - Real unit tests MUST cover edge cases, NaN telemetry, night-to-day transitions, leap years, and extreme temperatures.
   - Strict Test-Driven Development (TDD) workflow: write test -> verify failure -> implement -> verify pass.
3. **Resource Governance (Host Constraints)**:
   - Execution environment: Intel Core i5-7200U (2 cores, 4 threads), 8GB RAM, 1TB mechanical HDD.
   - Maximum Concurrent Processes: 1 (strictly sequential single-threaded execution queue; no parallel subagent spawns or concurrent worktrees).
   - Memory Limit: No process may allocate more than 3.5 GB of resident RAM.
   - Raw Dataset Access: The full 1.76M-row raw CSV (SHA-256 `eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0`, skipping corrupted row 1,767,915) MUST NEVER be loaded in bulk into memory or LLM prompt contexts; stream chunking or sampled datasets in `data/samples/` MUST be used.
*Rationale*: Resource constraints protect the host environment against thrashing and crashes, while clean code and test guards guarantee long-term codebase maintainability and reliability.

## The 8 Architectural Rooms & System Contracts

```
[ External Data Sources ] -> E1: DKA Solar Centre (Raw CSV) + E2: Open-Meteo (NWP Weather API)
                                         |
                                         v
+-------------------------------+                  +-------------------------------+
| Room 1: Data Pipeline         |                  | Room 2: Pure Physics Engine   |
| (data_pipeline/)              | ---------------> | (packages/solar_core/)        |
| - Ingestion & UTC shift (-9.5h)|                  | - Pure functions, zero I/O    |
| - Hourly resample (closed='R')|                  | - Solar position & clear-sky  |
| - Quality flags & clean data  |                  | - Faiman module temp & soiling|
+-------------------------------+                  +-------------------------------+
                |                                                  |
                v                                                  v
+-------------------------------+                  +-------------------------------+
| Room 4: Database Storage      |                  | Room 3: ML Training           |
| (db/)                         | <--------------- | (ml_training/)                |
| - PostgreSQL 16 schema        |                  | - M0-M4 models (clear-sky r)  |
| - Idempotent UPSERT contracts |                  | - model.json + metadata.json  |
+-------------------------------+                  +-------------------------------+
        |               ^                                          |
        |               |                                          v
        |       +---------------+                  +-------------------------------+
        |       | Room 5: Worker|                  | Room 8: Testing & QA Gates    |
        +-----> | (worker/)     |                  | (tests/)                      |
                | - replay_job  |                  | - Metamorphic Gate (MR1-MR8)  |
                | - soiling_job |                  | - Unit, edge, & boundary tests|
                | - forecast_job|                  +-------------------------------+
                +---------------+
                        |
                        v
        +-------------------------------+
        | Room 6: API Service           |
        | (api/ - FastAPI Read-Only)    |
        | - 8 analytical JSON endpoints |
        +-------------------------------+
                        |
                        v
        +-------------------------------+
        | Room 7: UI Dashboard          |
        | (ui/ - React + Vite + Recharts)|
        | - 3 synchronized analytical   |
        |   operational views           |
        +-------------------------------+
```

### Room Contracts & Dependencies
1. **Room 1 (`data_pipeline/`)**: Reads raw CSV data and Open-Meteo weather JSON. Emits clean parquet/CSV datasets with columns: `[ts_utc, poa_wm2, ghi_wm2, dni_wm2, dhi_wm2, temp_air_c, temp_module_c, wind_speed_ms, power_kw, quality_flag]`.
2. **Room 2 (`packages/solar_core/`)**: Pure library consumable by Rooms 1, 3, 5, and 8. Exposes modules: `config`, `physics`, `features`, `validator`, `soiling`, and `sim`.
3. **Room 3 (`ml_training/`)**: Consumes cleaned datasets from Room 1 and physics features from Room 2. Emits evaluated models strictly to `models/ACTIVE/model.json` and `models/ACTIVE/metadata.json`.
4. **Room 4 (`db/`)**: Houses relational tables (`plants`, `measurements`, `weather_forecast`, `model_forecast`, `plant_health_daily`, `alerts`). All ingestion queries MUST use deterministic `MAX(ts_utc)` reference clock rather than `NOW()`.
5. **Room 5 (`worker/`)**: Executes batch jobs (`replay_job`, `soiling_job`, `forecast_job`) using idempotent `ON CONFLICT DO UPDATE` queries.
6. **Room 6 (`api/`)**: FastAPI application providing read-only query endpoints. Emits structured JSON adhering strictly to `docs/openapi.json`.
7. **Room 7 (`ui/`)**: Single-page application consuming Room 6 API. Displays Plant Overview, Forecast vs. Actual, and Anomaly Inspection dashboards.
8. **Room 8 (`tests/`)**: Automated test suite executing pytest with coverage reporting and metamorphic verification.

## Development Workflow & Quality Gates

1. **Spec Kit Sequential Phase Gates**:
   - **Specification Gate (`spec.md`)**: Define user requirements, domain contracts, and acceptance criteria via `/speckit-specify` and `/speckit-clarify`.
   - **Architectural Plan Gate (`plan.md`)**: Formulate directory layout, data models, and component diagrams via `/speckit-plan`.
   - **Task Breakdown Gate (`tasks.md`)**: Generate dependency-ordered, single-responsibility tasks via `/speckit-tasks`.
   - **Implementation Gate**: Sequential coding via execution agent following `/speckit-implement`, running `pytest` continuously.
2. **Automated Multi-Guard Verification**:
   - `solar-physics-guard`: Validates compliance with DKASC Site 14 parameters, the 7 empirical decisions, Faiman temperature modeling, and MR1–MR8.
   - `clean-code-guard`: Validates pure functional isolation in `packages/solar_core/`, static typing, and absence of boilerplate AI comments.
   - `test-guard`: Validates 100% pytest pass rate, boundary condition coverage, and zero regressions.
3. **Model Promotion Gate**:
   - Model artifacts MUST satisfy both statistical thresholds (Test daytime RMSE $< 0.35$ kW, MAE $< 0.20$ kW) AND Metamorphic QA Gate pass rate $\ge 95\%$ before promotion to `models/ACTIVE/`.

## Governance

1. **Supreme Authority**:
   This constitution defines the non-negotiable architectural and engineering governance for Solar-Grid AI (v1.1). It supersedes all individual task instructions, documentation drafts, or temporary agent suggestions.
2. **Amendment Procedure**:
   Any modification, addition, or revocation of principles within this constitution requires:
   - Formal architectural justification documented in a change proposal.
   - Mathematical and empirical re-validation against the 8 Metamorphic Relations and DKASC Site 14 constants.
   - Semantic version bump according to strict versioning policy.
   - Update of the `LAST_AMENDED_DATE` metadata field.
3. **Semantic Versioning Policy**:
   - **MAJOR (X.0.0)**: Removal or backward-incompatible redefinition of any Core Principle, directory layout, or physics invariant.
   - **MINOR (1.X.0)**: Addition of new principles, new metamorphic relations (e.g., MR9+), or materially expanded quality gates.
   - **PATCH (1.0.X)**: Typographical corrections, clarifications, documentation formatting, and non-semantic adjustments.
4. **Compliance Verification**:
   Every code contribution, automated workflow, pull request, and agent task execution MUST be verified for constitutional compliance before acceptance. Non-compliant artifacts MUST be rejected and flagged for refactoring.

**Version**: 1.2.0 | **Ratified**: 2026-10-26 | **Last Amended**: 2026-10-31
