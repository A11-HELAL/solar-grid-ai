# Tasks: Foundational Solar Core Configuration & Packaging

**Input**: Design documents from `specs/001-solar-core-config/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)

**Prerequisites**: `plan.md` (completed), `spec.md` (completed), `data-model.md` (completed), `contracts/` (completed)

**Organization**: Grouped into sequential phases and user story increments (US1, US2, US3) to enable independent implementation, rigorous TDD verification, and strict sequential execution per Constitution Principle I.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Independent file / module task
- **[Story]**: Associated User Story (`[US1]`, `[US2]`, `[US3]`)
- Clear file paths included in every task

---

## Phase 1: Setup & Packaging Infrastructure

**Purpose**: Project root packaging manifest, plant configuration file, and test suite initialization.

- [ ] T001 Create project packaging configuration in `pyproject.toml` using `setuptools.build_meta`, defining project metadata (`name = "solar-grid-ai"`, `version = "1.1.0"`), core dependencies (`pvlib>=0.10.0`, `pyyaml>=6.0`, `numpy>=1.24.0`, `pandas>=2.0.0`, `pydantic>=2.0.0`, `tzdata; platform_system == 'Windows'`), dev dependencies (`pytest>=7.0.0`, `pytest-cov>=4.0.0`), and package discovery for `solar_core*`
- [ ] T002 [P] Create verified DKASC Site 14 plant configuration in `plant_config.yaml` matching contract schema (`plant_id: "dka_01"`, `lat: -23.7618`, `lon: 133.8748`, `elevation_m: 545.0`, `tz: "Australia/Darwin"`, `capacity_kwp: 5.4`, `inverter_kw: 5.0`, `tilt_deg: 20.0`, `azimuth_deg: 0.0`, `gamma_per_c: -0.004`, `ref_temp_c: 25.0`, `calibration_factor: 0.92`, `night_clear_sky_threshold_kw: 0.1`, `max_short_gap_hours: 2`)
- [ ] T003 [P] Initialize unit test package structure by creating `tests/__init__.py` and `tests/unit/__init__.py`

---

## Phase 2: Foundational Core Module & Package Initialization

**Purpose**: Package initializer and version export prerequisite for domain modules.

- [ ] T004 Create package initializer `solar_core/__init__.py` exporting `CORE_VERSION = "1.1.0"`, `__version__ = "1.1.0"`, and `__all__` list exposing `PlantConfig`, `SoilingConfig`, `ValidatorConfig`, `load_plant_config`, `validate_plant_config`, `QUALITY_FLAGS`, `RAW_DKA_SHA256`, and `FEATURE_COLUMNS`

---

## Phase 3: User Story 1 - Immutable Plant Configuration & Physical Validation (Priority: P1) 🌟 MVP

**Goal**: Deliver the immutable `PlantConfig` dataclass and pure loader/validator functions enforcing DKASC Site 14 physical constraints and runtime immutability.

**Independent Test**: Execute `pytest tests/unit/test_config.py -k "test_plant_config or test_load_plant"` to verify successful loading of `plant_config.yaml`, immutability enforcement (`FrozenInstanceError`), and rejection of unphysical parameters (`ValueError`).

### Tests for User Story 1 (TDD First) 🧪

- [ ] T005 [P] [US1] Create unit test suite in `tests/unit/test_config.py` covering:
  - Default `PlantConfig` attribute values matching Site 14 constants
  - Immutability check asserting `FrozenInstanceError` when attempting attribute reassignment
  - Boundary validation rejecting unphysical parameters: latitude outside `[-90, 90]`, longitude outside `[-180, 180]`, elevation outside `[-500, 9000]`, capacity `capacity_kwp <= 0`, inverter `inverter_kw <= 0` or `inverter_kw > capacity_kwp`, tilt outside `[0, 90]`, azimuth outside `[0, 360]`, positive temperature coefficient `gamma_per_c >= 0`, calibration factor outside `[0.5, 1.5]`, non-positive night threshold, and invalid IANA timezone string
  - `load_plant_config` loading valid `plant_config.yaml`
  - `load_plant_config` raising `FileNotFoundError` for missing paths
  - `load_plant_config` raising `ValueError` on malformed YAML, non-dict payloads, or missing mandatory keys

### Implementation for User Story 1

- [ ] T006 [US1] Implement immutable dataclass `PlantConfig` in `solar_core/config.py` with `@dataclass(frozen=True, slots=True)`, DKASC Site 14 defaults, and `__post_init__` hook invoking validation
- [ ] T007 [US1] Implement pure validation function `validate_plant_config(config: PlantConfig) -> None` in `solar_core/config.py` enforcing all physical parameter boundaries and timezone validation via `zoneinfo.ZoneInfo`
- [ ] T008 [US1] Implement pure loader function `load_plant_config(path: Union[str, Path]) -> PlantConfig` in `solar_core/config.py` using `yaml.safe_load`, validating path existence, mandatory key presence, and instantiating `PlantConfig`

**Checkpoint**: User Story 1 is completely functional and independently testable. Core plant constants can be loaded and guaranteed immutable.

---

## Phase 4: User Story 2 - Subsystem Configurations & Canonical Contracts (Priority: P2)

**Goal**: Deliver immutable `SoilingConfig`, `ValidatorConfig`, and canonical contract constants (`QUALITY_FLAGS`, `RAW_DKA_SHA256`, `FEATURE_COLUMNS`).

**Independent Test**: Execute `pytest tests/unit/test_config.py -k "test_subsystem_configs or test_canonical_contracts"` to verify defaults, threshold inversion guards, and contract constant values.

### Tests for User Story 2 (TDD First) 🧪

- [ ] T009 [P] [US2] Add unit tests in `tests/unit/test_config.py` covering:
  - Default values for `SoilingConfig` (`min_poa_wm2 = 500.0`, `max_unclipped_power_kw = 4.95`, `min_valid_hours = 4`, `rolling_window_days = 7`, `baseline_clean_days = 14`, `watch_loss_pct = 2.0`, `clean_alert_loss_pct = 4.0`, `recovery_jump_pct = 2.0`, `fault_drop_pct = 10.0`)
  - Threshold validation in `SoilingConfig` rejecting `clean_alert_loss_pct <= watch_loss_pct` or non-positive thresholds
  - Immutability check asserting `FrozenInstanceError` on `SoilingConfig`
  - Default values for `ValidatorConfig` (`clear_sky_headroom_factor = 1.1`, `warn_intervention_rate_pct = 5.0`, `critical_intervention_rate_pct = 15.0`)
  - Threshold validation in `ValidatorConfig` rejecting `critical_intervention_rate_pct <= warn_intervention_rate_pct`
  - Immutability check asserting `FrozenInstanceError` on `ValidatorConfig`
  - Contract validation asserting `QUALITY_FLAGS == ("ok", "interpolated", "missing", "fault_suspect", "out_of_range")`
  - Contract validation asserting `RAW_DKA_SHA256 == "eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0"`
  - Contract validation asserting `FEATURE_COLUMNS` has exactly 12 ordered features (`"poa_wm2"`, `"temp_air_c"`, `"wind_ms"`, `"temp_module_c"`, `"clear_sky_kw"`, `"cloud_cover"`, `"zenith_deg"`, `"azimuth_deg"`, `"hour"`, `"day_of_year"`, `"power_kw_lag_1h"`, `"power_kw_lag_24h"`)

### Implementation for User Story 2

- [ ] T010 [US2] Implement immutable dataclasses `SoilingConfig` and `ValidatorConfig` in `solar_core/config.py` with `@dataclass(frozen=True, slots=True)` and threshold validation in `__post_init__`
- [ ] T011 [US2] Define canonical contract constants in `solar_core/config.py`: `CORE_VERSION`, `QUALITY_FLAGS`, `RAW_DKA_SHA256`, and `FEATURE_COLUMNS`

**Checkpoint**: User Stories 1 and 2 are fully integrated, providing domain constants and operational configs.

---

## Phase 5: User Story 3 - Packaging & Environment Integration (Priority: P3)

**Goal**: Verify editable package installation (`pip install -e .`) and seamless package-level exports.

**Independent Test**: Execute `python -c "import solar_core; assert solar_core.CORE_VERSION == '1.1.0'"` and verify all exports in `__all__` resolve correctly.

### Tests for User Story 3 🧪

- [ ] T012 [P] [US3] Add package integration tests in `tests/unit/test_config.py` asserting that `solar_core.__version__ == "1.1.0"`, `solar_core.CORE_VERSION == "1.1.0"`, and all symbols in `solar_core.__all__` are importable from `solar_core`

### Implementation for User Story 3

- [ ] T013 [US3] Install the package in editable mode via `pip install -e .` from repository root and verify zero build warnings

**Checkpoint**: `solar_core` is installed in editable mode and accessible from anywhere in the monorepo.

---

## Phase 6: Polish & Verification Quality Gate

**Purpose**: End-to-end verification across test suite, quickstart scenarios, and multi-guard compliance.

- [ ] T014 Execute full pytest suite `pytest tests/unit/test_config.py -v --tb=short` and verify 100% pass rate
- [ ] T015 Run all validation scenarios from `specs/001-solar-core-config/quickstart.md`
- [ ] T016 Audit implementation against `solar-physics-guard` (DKASC Site 14 constants, clipping guard 4.95 kW, 5 quality flags), `clean-code-guard` (zero DB/network/`now()`/`pickle`, frozen dataclasses), and `test-guard` (100% test pass rate)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Packaging (Phase 1)**: Independent, executed first.
- **Foundational Package Init (Phase 2)**: Depends on Phase 1.
- **User Story 1 (Phase 3)**: Depends on Phase 2. Core MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 3 (extends `solar_core/config.py`).
- **User Story 3 (Phase 5)**: Depends on Phase 4 (verifies full package exports and editable install).
- **Polish & QA Gates (Phase 6)**: Runs after all user story phases complete.

### Strict Sequential Execution Rule (Constitution Principle I)

Per Constitution Principle I, all tasks MUST execute in strict sequence:
`T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016`.
No parallel sub-agents or concurrent threads may be spawned.

---

## Implementation Strategy

### MVP Scope (Phase 1 through Phase 3)
Completing Phases 1–3 delivers the core plant configuration module, capable of reading and validating DKASC Site 14 parameters with full immutability and physical invariant enforcement.

### Incremental Delivery
1. **Increment 1 (MVP)**: `pyproject.toml`, `plant_config.yaml`, `PlantConfig`, `validate_plant_config`, `load_plant_config`, and comprehensive US1 tests.
2. **Increment 2**: `SoilingConfig`, `ValidatorConfig`, `QUALITY_FLAGS`, `RAW_DKA_SHA256`, `FEATURE_COLUMNS`, and US2 tests.
3. **Increment 3**: Package exports in `solar_core/__init__.py`, editable install verification, and US3 tests.
4. **Increment 4**: End-to-end quickstart script run and guard audit.
