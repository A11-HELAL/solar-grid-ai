# Feature Specification: Foundational Solar Core Configuration & Packaging

**Feature Branch**: `001-solar-core-config`

**Created**: 2026-10-26

**Status**: Draft

**Input**: User description: "Build the foundational configuration module `solar_core/config.py`, package initializer `solar_core/__init__.py` (exposing `CORE_VERSION = "1.1.0"`), `pyproject.toml` (for editable install `pip install -e .`), and root `plant_config.yaml` for DKASC Site 14 (`dka_01`). Requirements: 1. Define immutable (`frozen=True`) dataclasses in `solar_core/config.py`: `PlantConfig`, `SoilingConfig`, and `ValidatorConfig`. 2. Define canonical `QUALITY_FLAGS`, `RAW_DKA_SHA256`, and `FEATURE_COLUMNS` contract. 3. Implement pure function `load_plant_config(path: Path) -> PlantConfig` using PyYAML with strict validation against impossible physical values."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Immutable Plant Configuration & Physical Validation (Priority: P1)

Solar-Grid AI core engineers and downstream physics modules need an authoritative, immutable plant configuration representation that loads from file, validates all physical invariants, and protects against accidental runtime mutation.

**Why this priority**: Without an authoritative, physically validated plant configuration, no downstream physics calculations (clear-sky modeling, solar geometry, thermal derating) or data transformations can operate safely.

**Independent Test**: Load valid and invalid YAML files via the configuration loader; verify that valid configurations instantiate an immutable object and that physically impossible values (e.g., negative capacity, out-of-bounds tilt) immediately raise clear validation errors.

**Acceptance Scenarios**:

1. **Given** a valid YAML file containing DKASC Site 14 constants, **When** loaded via `load_plant_config`, **Then** return a `PlantConfig` instance matching all plant parameters with `frozen=True` immutability.
2. **Given** an instantiated `PlantConfig`, **When** any field mutation is attempted (e.g., `config.capacity_kwp = 10.0`), **Then** raise an immutability exception (`FrozenInstanceError`).
3. **Given** a YAML file containing physically impossible values (e.g., `capacity_kwp <= 0`, `tilt_deg < 0` or `tilt_deg > 90`, `gamma_per_c >= 0`), **When** `load_plant_config` is called, **Then** raise a descriptive `ValueError` identifying the invalid parameter.

---

### User Story 2 - Subsystem Configurations & Contract Definitions (Priority: P2)

ML engineers, quality assurance routines, and soiling detection jobs need dedicated immutable configuration contracts for soiling analysis, data quality validation, canonical telemetry quality flags, and machine learning feature columns.

**Why this priority**: Downstream data pipelines, soiling algorithms, and training loops require standardized constants and thresholds to prevent silent contract drift across monorepo boundaries.

**Independent Test**: Instantiate `SoilingConfig` and `ValidatorConfig` with default and custom values, verify immutability, and assert membership and order in `QUALITY_FLAGS`, `RAW_DKA_SHA256`, and `FEATURE_COLUMNS`.

**Acceptance Scenarios**:

1. **Given** standard soiling detection thresholds, **When** `SoilingConfig` is instantiated, **Then** provide verified defaults: `min_poa_wm2 = 500.0`, `max_unclipped_power_kw = 4.95`, `min_valid_hours = 4`, `rolling_window_days = 7`, `baseline_clean_days = 14`, `watch_loss_pct = 2.0`, `clean_alert_loss_pct = 4.0`, `recovery_jump_pct = 2.0`, `fault_drop_pct = 10.0`.
2. **Given** quality validator parameters, **When** `ValidatorConfig` is instantiated, **Then** provide verified defaults: `clear_sky_headroom_factor = 1.1`, `warn_intervention_rate_pct = 5.0`, `critical_intervention_rate_pct = 15.0`.
3. **Given** the telemetry quality flagging contract, **When** referencing `QUALITY_FLAGS`, **Then** return the immutable tuple `("ok", "interpolated", "missing", "fault_suspect", "out_of_range")`.
4. **Given** the raw DKASC dataset hash contract, **When** referencing `RAW_DKA_SHA256`, **Then** return `"eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0"`.
5. **Given** the model training feature contract, **When** referencing `FEATURE_COLUMNS`, **Then** return an ordered tuple containing all required model input features.

---

### User Story 3 - Reproducible Packaging & Project Root Configuration (Priority: P3)

Developers and automated CI/CD runners need a standardized Python package definition and root plant configuration file to allow seamless editable installation (`pip install -e .`) and zero-configuration plant instantiation.

**Why this priority**: Eliminates Python path hacking, ensures `solar_core` is importable across all scripts and tests, and version-pins the core engine at `1.1.0`.

**Independent Test**: Install the package in editable mode within the target Python environment; verify that `import solar_core` succeeds and exposes `CORE_VERSION == "1.1.0"` alongside the configuration dataclasses.

**Acceptance Scenarios**:

1. **Given** a new environment, **When** `pip install -e .` is executed from the repository root, **Then** install `solar_core` successfully without build errors.
2. **Given** the installed package, **When** executing `import solar_core`, **Then** `solar_core.CORE_VERSION` equals `"1.1.0"`.
3. **Given** the repository root, **When** inspecting `plant_config.yaml`, **Then** contain complete, valid DKASC Site 14 parameters that parse cleanly via `load_plant_config("plant_config.yaml")`.

---

### Edge Cases

- **Non-existent or unreadable file**: Calling `load_plant_config(path)` with a path that does not exist MUST raise `FileNotFoundError` with the path indicated.
- **Empty or malformed YAML**: Passing an empty file or invalid YAML syntax MUST raise a descriptive `ValueError` or `yaml.YAMLError`.
- **Missing mandatory fields**: Omission of any required plant parameter in the YAML dictionary MUST raise a `ValueError` indicating the missing field name.
- **Out-of-range physical coordinates**: Latitude outside `[-90.0, 90.0]` or longitude outside `[-180.0, 180.0]` MUST raise `ValueError`.
- **Inverted thermal coefficient**: A non-negative temperature coefficient (`gamma_per_c >= 0.0`) MUST raise `ValueError` as PV power output decreases with cell heating.
- **Inverter capacity exceeding array**: An inverter capacity (`inverter_kw`) that exceeds the nameplate DC capacity (`capacity_kwp`) MUST raise `ValueError`.
- **Invalid IANA Timezone**: An unparseable or unrecognized timezone string in `tz` MUST be rejected with a `ValueError`.
- **Threshold inversion**: In `SoilingConfig`, if `clean_alert_loss_pct <= watch_loss_pct`, validation MUST raise `ValueError`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an immutable (`frozen=True`) dataclass `PlantConfig` in `solar_core/config.py` with default parameters corresponding to DKASC Site 14 (`plant_id="dka_01"`, `lat=-23.7618`, `lon=133.8748`, `elevation_m=545.0`, `tz="Australia/Darwin"`, `capacity_kwp=5.4`, `inverter_kw=5.0`, `tilt_deg=20.0`, `azimuth_deg=0.0`, `gamma_per_c=-0.004`, `ref_temp_c=25.0`, `calibration_factor=0.92`, `night_clear_sky_threshold_kw=0.1`, `max_short_gap_hours=2`).
- **FR-002**: System MUST provide an immutable (`frozen=True`) dataclass `SoilingConfig` in `solar_core/config.py` with default parameters (`min_poa_wm2=500.0`, `max_unclipped_power_kw=4.95`, `min_valid_hours=4`, `rolling_window_days=7`, `baseline_clean_days=14`, `watch_loss_pct=2.0`, `clean_alert_loss_pct=4.0`, `recovery_jump_pct=2.0`, `fault_drop_pct=10.0`).
- **FR-003**: System MUST provide an immutable (`frozen=True`) dataclass `ValidatorConfig` in `solar_core/config.py` with default parameters (`clear_sky_headroom_factor=1.1`, `warn_intervention_rate_pct=5.0`, `critical_intervention_rate_pct=15.0`).
- **FR-004**: System MUST define constant `QUALITY_FLAGS` as an immutable tuple `("ok", "interpolated", "missing", "fault_suspect", "out_of_range")`.
- **FR-005**: System MUST define constant `RAW_DKA_SHA256 = "eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0"`.
- **FR-006**: System MUST define constant `FEATURE_COLUMNS` as an immutable tuple contract of required model feature names (`poa_wm2`, `temp_air_c`, `wind_ms`, `temp_module_c`, `clear_sky_kw`, `cloud_cover`, `zenith_deg`, `azimuth_deg`, `hour`, `day_of_year`, `power_kw_lag_1h`, `power_kw_lag_24h`).
- **FR-007**: System MUST implement a pure function `load_plant_config(path: Union[str, Path]) -> PlantConfig` that reads a YAML file and validates physical realism before constructing `PlantConfig`.
- **FR-008**: Validation within `load_plant_config` MUST enforce:
  - `lat` within `[-90.0, 90.0]`
  - `lon` within `[-180.0, 180.0]`
  - `elevation_m` within `[-500.0, 9000.0]`
  - `capacity_kwp > 0.0`
  - `0.0 < inverter_kw <= capacity_kwp`
  - `tilt_deg` within `[0.0, 90.0]`
  - `azimuth_deg` within `[0.0, 360.0]` (or `[-180.0, 180.0]`)
  - `gamma_per_c` within `[-0.015, -0.0001]`
  - `ref_temp_c` within `[0.0, 50.0]`
  - `calibration_factor` within `[0.5, 1.5]`
  - `night_clear_sky_threshold_kw > 0.0`
  - `max_short_gap_hours > 0`
  - Valid timezone recognized by Python standard library `zoneinfo`.
- **FR-009**: Package initializer `solar_core/__init__.py` MUST export `CORE_VERSION = "1.1.0"` and expose `PlantConfig`, `SoilingConfig`, `ValidatorConfig`, `load_plant_config`, `QUALITY_FLAGS`, `RAW_DKA_SHA256`, and `FEATURE_COLUMNS`.
- **FR-010**: System MUST provide a root `pyproject.toml` specifying project metadata, package directory mapping, and required dependencies (`pvlib>=0.10.0`, `pyyaml>=6.0`, `numpy>=1.24.0`, `pandas>=2.0.0`, `pydantic>=2.0.0`).
- **FR-011**: System MUST provide a root `plant_config.yaml` populated with verified DKASC Site 14 configuration values.

### Key Entities

- **PlantConfig**: Encapsulates immutable array geometry, nameplate ratings, thermal loss coefficients, calibration factors, and timezone metadata for a solar facility.
- **SoilingConfig**: Encapsulates operational thresholds, clipping filter criteria, rolling evaluation window sizes, and progressive cleaning alarm limits.
- **ValidatorConfig**: Encapsulates data cleansing tolerances, physical headroom limits, and operational intervention alert rates.
- **QualityFlag Contract**: Canonical classification states representing telemetry observation validity.
- **FeatureColumns Contract**: Canonical schema contract for machine learning feature inputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of physical validation constraints execute in under 10 milliseconds when loading configuration.
- **SC-002**: 100% of runtime attribute modification attempts on instantiated configuration dataclasses fail with an immutability exception.
- **SC-003**: 0% unhandled exceptions on invalid or corrupted YAML input files; all invalid inputs trigger explicit, informative validation errors.
- **SC-004**: Zero external network or database dependencies required to load, validate, or serialize configuration objects.
- **SC-005**: Package installation via `pip install -e .` succeeds in under 15 seconds in standard Python 3.10+ virtual environments.
- **SC-006**: 100% compliance with Solar-Grid AI Constitution v1.1.0 and `solar-physics-guard` specifications.

## Assumptions

- Target execution environment runs Python 3.10 or higher.
- `zoneinfo` from the Python standard library is used for timezone string validation (backed by `tzdata` if running on Windows).
- All physical validation rules operate as pure functions without side effects or logging overhead.
- Raw CSV files from `data/raw/` are never accessed during configuration loading; only the cryptographic hash constant `RAW_DKA_SHA256` is defined for downstream validation.
