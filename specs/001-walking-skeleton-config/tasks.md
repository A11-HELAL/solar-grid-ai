---
description: "Task list for 001-walking-skeleton-config implementation"
---

# Tasks: Foundational Walking Skeleton & Room 2 Configuration Module

**Input**: Design documents from `/specs/001-walking-skeleton-config/` (`spec.md`, `plan.md`, `data-model.md`, `research.md`, `contracts/`, `quickstart.md`)
**Constitution**: Solar-Grid AI v1.2.0 (Strict sequential single-threaded execution, 8 rooms, pure physics in `packages/solar_core`, zero generic `src/`)
**TDD Enforcement**: Strict test-first workflow for User Story 2 (`tests/test_config.py` written and verified failing before implementing `packages/solar_core/config.py`)

## Phase 1: Setup (Shared Environment & Packaging)

**Purpose**: Establish baseline environment dependencies and package resolution for the 8-room monorepo.

- [X] T001 Establish baseline dependencies (`pvlib>=0.10.0`, `pyyaml>=6.0`, `numpy>=1.24.0`, `pandas>=2.0.0`, `pydantic>=2.0.0`, `fastapi>=0.110.0`, `uvicorn>=0.28.0`, `xgboost>=2.0.0`, `pytest>=8.0.0`) in `requirements.txt`
- [X] T002 Establish local package definition for Room 2 in `packages/solar_core/pyproject.toml`
- [X] T003 Establish repository root packaging configuration for editable installation in `pyproject.toml`

---

## Phase 2: Foundational (Operational Storage & Test Harness)

**Purpose**: Core operational directories and test infrastructure that block user story implementation.

- [X] T004 Establish operational data and model staging directory markers in `data/raw/.gitkeep`, `data/processed/.gitkeep`, and `models/ACTIVE/.gitkeep`
- [X] T005 Setup pytest test configuration and shared fixtures in `tests/conftest.py`
- [X] T006 Initialize package root exports exposing `CORE_VERSION = "1.1.0"` in `packages/solar_core/__init__.py`

---

## Phase 3: User Story 1 - Multi-Track Walking Skeleton & Directory Initialization (Priority: P1)

**Goal**: Scaffold the complete 8-room decoupled layout with package initializers and clean stubs to enable concurrent engineering tracks.
**Independent Test**: Verify file tree across all 8 rooms; confirm zero generic `src/` directory exists.

- [X] T007 [P] [US1] Create Room 1 directory and module stubs in `data_pipeline/__init__.py`, `data_pipeline/ingest.py`, and `data_pipeline/clean.py`
- [X] T008 [P] [US1] Create Room 2 pure physics module stubs in `packages/solar_core/physics.py`, `packages/solar_core/features.py`, `packages/solar_core/validator.py`, `packages/solar_core/soiling.py`, and `packages/solar_core/sim.py`
- [X] T009 [P] [US1] Create Room 3 ML training module stubs in `ml_training/__init__.py`, `ml_training/data_loader.py`, `ml_training/train.py`, `ml_training/evaluate.py`, and `ml_training/export.py`
- [X] T010 [P] [US1] Create Room 4 database schema directory and stub in `db/__init__.py` and `db/init/01_schema.sql`
- [X] T011 [P] [US1] Create Room 5 background worker module stubs in `worker/__init__.py` and `worker/jobs.py`
- [X] T012 [P] [US1] Create Room 6 analytical API module stubs in `api/__init__.py` and `api/main.py`
- [X] T013 [P] [US1] Create Room 7 UI frontend manifest and entry stubs in `ui/package.json` and `ui/src/App.tsx`
- [X] T014 [US1] Verify 8-room directory layout and assert zero presence of generic `src/` directory using validation script in `tests/__init__.py`

**Checkpoint**: 8-room skeleton complete; all team tracks can import modules and develop in parallel.

---

## Phase 4: User Story 2 - Immutable Plant Configuration & Physical Validation (Priority: P1)

**Goal**: Provide pure, immutable `PlantConfig` dataclass and `load_plant_config` enforcing strict physical bounds under strict TDD.
**Independent Test**: Execute `pytest tests/test_config.py` confirming 100% pass rate on immutability and physical bound rejections.

### Tests for User Story 2 (TDD Mandatory - Write First)
- [X] T015 [US2] Write unit tests in `tests/test_config.py` covering valid configuration parsing, `FrozenInstanceError` on attribute mutations, `FileNotFoundError` on missing paths, unphysical capacity (`inverter >= capacity` or `inverter <= 0`), out-of-range tilt (`tilt < 0` or `tilt > 90`), positive thermal coefficient ($\gamma \ge 0$), invalid calibration factor (`calibration <= 0` or `calibration > 1.5`), and malformed YAML
- [X] T016 [US2] Execute `pytest tests/test_config.py` and confirm all tests fail with `ImportError` or `ModuleNotFoundError` prior to implementation (Red Phase)

### Implementation for User Story 2
- [X] T017 [US2] Implement immutable `PlantConfig` dataclass (`frozen=True, slots=True`) with DKASC Site 14 defaults in `packages/solar_core/config.py`
- [X] T018 [US2] Implement pure function `load_plant_config(path: Union[str, Path]) -> PlantConfig` with physical boundary validation raising `ValueError` and `FileNotFoundError` in `packages/solar_core/config.py`
- [X] T019 [US2] Export `PlantConfig` and `load_plant_config` in `packages/solar_core/__init__.py`
- [X] T020 [US2] Execute `pytest tests/test_config.py` and confirm all 10 tests pass (Green Phase)

**Checkpoint**: Pure physics configuration engine in Room 2 is verified, immutable, and physically guarded.

---

## Phase 5: User Story 3 - Authoritative Root Plant Constants (Priority: P2)

**Goal**: Codify locked DKASC Site 14 (`dka_01`) empirical constants in `plant_config.yaml` at the repository root.
**Independent Test**: Load `plant_config.yaml` via `load_plant_config("plant_config.yaml")` and assert exact parameter match.

- [X] T021 [US3] Create authoritative DKASC Site 14 configuration file locking plant (`dka_01`, lat -23.7618, lon 133.8748, elev 545.0, tz Australia/Darwin), array (capacity 5.4 kWp, inverter 5.0 kW, tilt 20.0 deg, azimuth 0.0 deg), and physics (gamma -0.004, ref_temp 25.0, calibration 0.92, night_threshold 0.1) in `plant_config.yaml`
- [X] T022 [US3] Add integration test in `tests/test_config.py` verifying that repository root `plant_config.yaml` loads cleanly and satisfies all Site 14 values

**Checkpoint**: Root configuration established as single source of truth for plant constants.

---

## Phase 6: User Story 4 - Baseline Dependencies & API Contract Verification (Priority: P3)

**Goal**: Establish reproducible dependencies and verify OpenAPI 3.0 contract for the 8 analytical endpoints.
**Independent Test**: Parse `docs/openapi.json` asserting 8 endpoints and valid schema structure.

- [X] T023 [US4] Author OpenAPI 3.0 specification covering the 8 analytical endpoints (`/health`, `/plants`, `/forecast`, `/measurements`, `/health`, `/alerts`, `/model-health`, and `/measurements` POST) in `docs/openapi.json`
- [X] T024 [US4] Add contract verification test in `tests/test_contract.py` asserting `docs/openapi.json` exists and defines valid OpenAPI 3.0 schemas for all 8 analytical endpoints

**Checkpoint**: Contract-first API specifications locked for backend and frontend integration tracks.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification and quality gate audits across all rooms.

- [X] T025 Execute end-to-end validation scenarios from `specs/001-walking-skeleton-config/quickstart.md`
- [X] T026 Audit codebase compliance against `clean-code-guard` (small pure functions, strict typing, zero AI fluff comments) in `packages/solar_core/config.py`
- [X] T027 Run full test suite `pytest tests/ -v` to ensure 100% pass rate under single-threaded execution

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Story 1 (Phase 3)**: Depends on Foundational completion. Sets up the 8-room skeleton.
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion. Executes strict TDD (tests T015-T016 before implementation T017-T020).
- **User Story 3 (Phase 5)**: Depends on User Story 2 completion. Uses `load_plant_config` to validate root `plant_config.yaml`.
- **User Story 4 (Phase 6)**: Depends on Setup completion. Validates API contract.
- **Polish (Phase 7)**: Depends on all user stories completion.

### User Story Dependencies
- **US1 (P1)**: Independent of US2/US3/US4. Scaffolds room directories.
- **US2 (P1)**: Independent of US3/US4. Implements and tests `packages/solar_core/config.py`.
- **US3 (P2)**: Depends on US2 (`load_plant_config` is used to verify `plant_config.yaml`).
- **US4 (P3)**: Independent of US2/US3. Establishes `docs/openapi.json`.

---

## Implementation Strategy (Sequential Single-Threaded Delivery)

1. **Step 1: Setup & Foundation (T001-T006)**: Lock dependencies and test framework.
2. **Step 2: Walking Skeleton MVP (T007-T014)**: Create all 8 room directories, initializers, and clean stubs.
3. **Step 3: Strict TDD for Room 2 Config (T015-T020)**:
   - Write failing test suite `tests/test_config.py`.
   - Implement `PlantConfig` and `load_plant_config` in `packages/solar_core/config.py`.
   - Run tests to reach Green state.
4. **Step 4: Authoritative Constants (T021-T022)**: Create root `plant_config.yaml` and verify against Site 14.
5. **Step 5: API Contract (T023-T024)**: Lock `docs/openapi.json`.
6. **Step 6: Polish (T025-T027)**: Run quickstart scenarios, audit clean-code guard, run full pytest suite.
