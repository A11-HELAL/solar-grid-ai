# Implementation Plan: Foundational Walking Skeleton & Room 2 Configuration Module

**Branch**: `001-walking-skeleton-config` | **Date**: 2026-10-31 | **Spec**: [specs/001-walking-skeleton-config/spec.md](spec.md)

**Input**: Feature specification from `/specs/001-walking-skeleton-config/spec.md`

## Summary

Establish the physical monorepo foundation for Solar-Grid AI v1.1 adhering strictly to Constitution v1.2.0:
1. Scaffold the complete 8-room directory layout (`data_pipeline/`, `packages/solar_core/`, `ml_training/`, `db/`, `worker/`, `api/`, `ui/`, `tests/`) alongside operational folders (`data/raw/`, `data/processed/`, `models/ACTIVE/`) with zero generic `src/` directory.
2. Initialize Room 2 pure physics stubs (`physics.py`, `features.py`, `validator.py`, `soiling.py`, `sim.py`) and Room 3 ML training stubs (`data_loader.py`, `train.py`, `evaluate.py`, `export.py`).
3. Author the canonical `plant_config.yaml` at the repository root locking DKASC Site 14 (`dka_01`) empirical constants.
4. Implement `packages/solar_core/config.py` with an immutable (`frozen=True`) `PlantConfig` dataclass and a pure `load_plant_config(path)` function enforcing physical invariant bounds.
5. Create locked `requirements.txt` and establish `docs/openapi.json` contract for the 8 analytical API endpoints.
6. Implement comprehensive unit tests in `tests/test_config.py`.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Standard library (`dataclasses`, `pathlib`, `typing`, `zoneinfo`), `PyYAML >= 6.0` (for configuration parsing), `pytest >= 8.0` (for test execution)
**Storage**: File-based YAML (`plant_config.yaml`), local staging directories (`data/raw/`, `data/processed/`, `models/ACTIVE/`)
**Testing**: `pytest`
**Target Platform**: Windows 10 / Linux (x86_64, host: Intel Core i5-7200U, 8GB RAM, 1TB mechanical HDD)
**Project Type**: Decoupled Monolith (Pure library package + multi-service architecture)
**Performance Goals**: Unit test suite runs in <100ms; configuration loading completes in <5ms; zero CPU spin or background thread contention
**Constraints**: Single-threaded execution; resident memory allocation <50MB for configuration routines; pure functions with zero DB/network/clock calls
**Scale/Scope**: 8 architectural rooms, 14 module stub files, 1 root configuration, 1 test suite with 10 unit tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitutional Pillar | Requirement | Compliance Analysis | Status |
| :--- | :--- | :--- | :---: |
| **I. 8-Room Decoupled Monolith** | Never use generic `src/`; strictly place code in 8 rooms | Scaffolds Room 1 to 8; zero `src/` folder created at root | **PASSED** |
| **II. Pure Physics Engine** | 100% pure functions in Room 2; zero DB, network, system clock (`datetime.now()`), or pickle | `PlantConfig` and `load_plant_config` use standard library + PyYAML; no I/O side effects, no system clock | **PASSED** |
| **III. Canonical Plant Constants** | `plant_config.yaml` locks DKASC Site 14 (`dka_01`) constants | Exactly incorporates capacity 5.4 kWp, inverter 5.0 kW, tilt 20.0°, azimuth 0.0°, $\gamma = -0.004$/°C, calibration factor 0.92, night threshold 0.1 kW | **PASSED** |
| **IV. Data & Timezone Standards** | UTC timestamps, no `fillna(0)`, quality flags | Establishes `data/raw/` and `data/processed/` boundaries; no zero-filling | **PASSED** |
| **V. ML & Validation Rules** | Portable JSON export, H1-H5 guardrails, MR1-MR8 gate | Prepares Room 3 stubs (`export.py`, `train.py`) and Room 2 `validator.py` stub | **PASSED** |
| **VI. Clean Code & Test Guard** | Pure functions, strict typing, zero AI fluff, real unit tests | Full typing hints; zero chatty comments; 10 edge tests in `tests/test_config.py` | **PASSED** |

## Project Structure

### Documentation (this feature)

```text
specs/001-walking-skeleton-config/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Phase 0 architectural decisions
├── data-model.md        # Phase 1 data entities and structural skeleton
├── quickstart.md        # Phase 1 verification and execution guide
├── contracts/
│   ├── plant-config-schema.md # plant_config.yaml schema contract
│   └── module-interface.md    # packages/solar_core/config.py API contract
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
/ (Repository Root)
├── plant_config.yaml                  # Authoritative DKASC Site 14 physical constants
├── requirements.txt                   # Baseline locked project dependencies
├── pyproject.toml                     # Root package configuration for packages/solar_core
├── docs/
│   ├── SG_Master_Spec.md              # Master specification
│   ├── SG_Data_Spec.md                # Data pipeline specification
│   └── openapi.json                   # OpenAPI 3.0 contract (8 endpoints)
├── data/
│   ├── raw/.gitkeep                   # Raw DKA CSV storage location
│   └── processed/.gitkeep             # Hourly resampled datasets
├── models/
│   └── ACTIVE/.gitkeep                # Production model destination
├── data_pipeline/                     # Room 1
│   ├── __init__.py
│   ├── ingest.py                      # Data ingestion stub
│   └── clean.py                       # Data clean & resample stub
├── packages/
│   └── solar_core/                    # Room 2: Pure Physics Engine
│       ├── __init__.py                # Package exports (__version__, PlantConfig, load_plant_config)
│       ├── pyproject.toml             # Local package definition
│       ├── config.py                  # PlantConfig dataclass & load_plant_config implementation
│       ├── physics.py                 # Pure solar position & clear-sky stub
│       ├── features.py                # Pure feature transformation stub
│       ├── validator.py               # H1-H5 guardrails stub
│       ├── soiling.py                 # Daily PR & soiling loss stub
│       └── sim.py                     # Synthetic PV simulation stub
├── ml_training/                       # Room 3: ML Training
│   ├── __init__.py
│   ├── data_loader.py                 # Training data loader stub
│   ├── train.py                       # M0-M4 training harness stub
│   ├── evaluate.py                    # Evaluation & metrics stub
│   └── export.py                      # Model JSON serialization stub
├── db/                                # Room 4: Relational Persistence
│   ├── __init__.py
│   └── init/
│       └── 01_schema.sql              # PostgreSQL 16 schema stub
├── worker/                            # Room 5: Background Worker
│   ├── __init__.py
│   └── jobs.py                        # replay_job, soiling_job, forecast_job stub
├── api/                               # Room 6: Analytical API
│   ├── __init__.py
│   └── main.py                        # FastAPI application entry stub
├── ui/                                # Room 7: Frontend UI
│   ├── package.json                   # Frontend manifest stub
│   └── src/
│       └── App.tsx                    # React UI entry stub
└── tests/                             # Room 8: Testing & QA Gates
    ├── __init__.py
    ├── conftest.py                    # Pytest fixtures
    └── test_config.py                 # Room 2 configuration unit tests
```

**Structure Decision**: Fully decoupled 8-room monorepo matching Constitution Principle I. Eliminates generic `src/`, encapsulates pure physics within `packages/solar_core/`, and provides clean module entry points for concurrent team development.

## Unit Test Design (`tests/test_config.py`)

The test suite will cover the following 10 test cases:
1. `test_load_plant_config_valid()`: Loads `plant_config.yaml` from root; validates all Site 14 fields match exact specification (`dka_01`, 5.4 kWp, 5.0 kW, 20.0° tilt, -0.004/°C gamma, 0.92 calibration factor).
2. `test_plant_config_immutability()`: Instantiates `PlantConfig`; asserts that modifying any field (e.g., `cfg.capacity_kwp = 10.0`) raises `dataclasses.FrozenInstanceError`.
3. `test_load_plant_config_missing_file()`: Verifies that passing a non-existent path raises `FileNotFoundError`.
4. `test_load_plant_config_positive_gamma()`: Verifies that $\gamma \ge 0.0$ (e.g., `gamma_per_c: 0.004`) raises `ValueError`.
5. `test_load_plant_config_negative_tilt()`: Verifies that `tilt_deg < 0.0` raises `ValueError`.
6. `test_load_plant_config_tilt_over_90()`: Verifies that `tilt_deg > 90.0` raises `ValueError`.
7. `test_load_plant_config_inverter_exceeds_capacity()`: Verifies that `inverter_ac_cap_kw >= capacity_kwp` (or $inverter \le 0$) raises `ValueError`.
8. `test_load_plant_config_invalid_calibration_factor()`: Verifies that `calibration_factor <= 0.0` or `calibration_factor > 1.5` raises `ValueError`.
9. `test_load_plant_config_malformed_yaml()`: Verifies that malformed or non-dictionary YAML content raises `ValueError`.
10. `test_load_plant_config_missing_fields()`: Verifies that omission of required keys raises `ValueError`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| *None* | *Fully compliant with Constitution v1.2.0* | *No constitutional exceptions requested* |
