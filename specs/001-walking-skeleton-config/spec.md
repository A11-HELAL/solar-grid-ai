# Feature Specification: Foundational Walking Skeleton & Room 2 Configuration Module

**Feature Branch**: `001-walking-skeleton-config`

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Build the foundational Walking Skeleton and Room 2 Configuration Module (001-walking-skeleton-config): 1. Initialize the 8-room directory layout (data_pipeline, packages/solar_core, ml_training, db, worker, api, ui, tests, data/raw, data/processed, models/ACTIVE) with empty __init__.py and stub files so all team tracks can work in parallel. 2. Create plant_config.yaml at the repository root containing the locked DKASC Site 14 (dka_01) physical constants. 3. Implement packages/solar_core/config.py with a pure, immutable PlantConfig dataclass (frozen=True) and a load_plant_config(path) function that validates physical bounds (capacity_kwp > inverter_ac_cap_kw > 0, tilt in [0, 90], calibration_factor in (0, 1.5]) and raises ValueError on invalid inputs. 4. Establish requirements.txt and verify docs/openapi.json contract existence."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Track Walking Skeleton & Directory Initialization (Priority: P1)

Solar-Grid AI engineers, data pipeline developers, ML practitioners, API developers, and QA teams need a fully scaffolded 8-room monorepo directory layout with standard entry points, data staging directories, and active model locations so that independent engineering tracks can work concurrently without merge conflicts or missing package paths.

**Why this priority**: Without an established physical directory skeleton and module roots, no parallel engineering can occur, import paths will diverge, and automated tooling will lack canonical boundaries.

**Independent Test**: Inspect the repository file tree; verify that all 8 rooms (`data_pipeline/`, `packages/solar_core/`, `ml_training/`, `db/`, `worker/`, `api/`, `ui/`, `tests/`) and operational folders (`data/raw/`, `data/processed/`, `models/ACTIVE/`) exist with valid package initializers and baseline stub files.

**Acceptance Scenarios**:

1. **Given** a clean workspace clone, **When** examining the directory tree, **Then** all 8 rooms exist with their respective `__init__.py` or stub files, and no generic `src/` directory exists.
2. **Given** the repository root, **When** checking data storage boundaries, **Then** `data/raw/`, `data/processed/`, and `models/ACTIVE/` are initialized with appropriate `.gitkeep` markers.
3. **Given** any development track (data engineering, backend, ML), **When** importing modules across room boundaries, **Then** `packages/solar_core` is recognized as a modular package.

---

### User Story 2 - Immutable Plant Configuration & Strict Physical Invariant Validation (Priority: P1)

Solar physics researchers, downstream data pipelines, and machine learning models need an immutable, pure domain configuration object (`PlantConfig`) that strictly rejects physically impossible values and guarantees runtime immutability.

**Why this priority**: Physical invariants (such as array capacity exceeding inverter rating, positive tilt angles, and bounded calibration factors) are non-negotiable. Loading corrupt or unphysical plant parameters corrupts all downstream clear-sky computations and model training.

**Independent Test**: Load a valid configuration file to assert an immutable `PlantConfig` instance; attempt in-place field mutations to verify `FrozenInstanceError`; pass invalid parameter files to verify descriptive `ValueError` triggers.

**Acceptance Scenarios**:

1. **Given** valid DKASC Site 14 parameters, **When** instantiating `PlantConfig`, **Then** return an immutable instance with `frozen=True` where attributes cannot be altered post-instantiation.
2. **Given** an invalid capacity ratio (`capacity_kwp <= inverter_ac_cap_kw` or `inverter_ac_cap_kw <= 0`), **When** executing `load_plant_config`, **Then** raise a `ValueError` indicating the invalid capacity or inverter rating.
3. **Given** an out-of-bounds tilt angle (`tilt < 0` or `tilt > 90`), **When** executing `load_plant_config`, **Then** raise a `ValueError` detailing the invalid tilt boundary.
4. **Given** an out-of-bounds calibration factor (`calibration_factor <= 0.0` or `calibration_factor > 1.5`), **When** executing `load_plant_config`, **Then** raise a `ValueError` detailing the invalid calibration factor.
5. **Given** an unphysical temperature coefficient ($\gamma \ge 0.0$), **When** executing `load_plant_config`, **Then** raise a `ValueError` confirming that PV efficiency degrades with temperature.

---

### User Story 3 - Authoritative Root Plant Constants (Priority: P2)

Operators, workers, and pipelines need an authoritative configuration file (`plant_config.yaml`) at the repository root codifying DKASC Site 14 (`dka_01`) empirical constants.

**Why this priority**: Prevents magic numbers from proliferating across codebases by anchoring all physical algorithms to an audited single source of truth.

**Independent Test**: Load `plant_config.yaml` using `load_plant_config("plant_config.yaml")` and verify that all parsed fields match the audited DKASC Site 14 specification.

**Acceptance Scenarios**:

1. **Given** `plant_config.yaml` at repository root, **When** loaded, **Then** all values match Site 14: `plant_id: "dka_01"`, `capacity_kwp: 5.4`, `inverter_ac_cap_kw: 5.0`, `tilt_deg: 20.0`, `azimuth_deg: 0.0`, `gamma_per_c: -0.004`, `calibration_factor: 0.92`, `night_threshold_kw: 0.1`, `tz: "Australia/Darwin"`.
2. **Given** a non-existent file path, **When** `load_plant_config` is called, **Then** raise `FileNotFoundError` with the missing path.

---

### User Story 4 - Baseline Dependencies & API Contract Verification (Priority: P3)

Developers and continuous integration runners need a locked `requirements.txt` file specifying core project dependencies and automated verification that the API contract specification (`docs/openapi.json`) exists.

**Why this priority**: Establishes reproducible local development environments and enforces the contract-first architecture required for API and UI teams.

**Independent Test**: Verify `requirements.txt` can be parsed without version conflicts, and verify that `docs/openapi.json` is present and valid JSON according to OpenAPI 3.0 standards.

**Acceptance Scenarios**:

1. **Given** the repository root, **When** inspecting `requirements.txt`, **Then** all core runtime dependencies (`pvlib`, `numpy`, `pandas`, `pyyaml`, `pydantic`, `fastapi`, `uvicorn`, `xgboost`, `pytest`) are specified with compatible version constraints.
2. **Given** the `docs/` directory, **When** checking `docs/openapi.json`, **Then** the file exists and defines valid OpenAPI 3.0 schema contracts for all 8 analytical endpoints.

---

### Edge Cases

- **Missing configuration file**: If the path provided to `load_plant_config` does not exist, the loader MUST raise `FileNotFoundError`.
- **Malformed YAML content**: If the configuration file contains invalid YAML syntax, the loader MUST raise `ValueError` with parse details.
- **Empty configuration file**: If the configuration file is empty or null, the loader MUST raise `ValueError` indicating empty configuration.
- **Missing mandatory keys**: If required fields (e.g., `capacity_kwp`, `lat`, `lon`) are omitted, the loader MUST raise `ValueError` naming the missing keys.
- **Type mismatch**: If numeric fields are supplied as non-numeric strings or lists, the loader MUST raise `ValueError` or `TypeError`.
- **Inverter capacity clipping boundary**: Inverter capacity `inverter_ac_cap_kw` must strictly satisfy $0.0 < \text{inverter\_ac\_cap\_kw} < \text{capacity\_kwp}$; equal or inverted values must raise `ValueError`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST establish the complete 8-room directory architecture: `data_pipeline/`, `packages/solar_core/`, `ml_training/`, `db/`, `worker/`, `api/`, `ui/`, `tests/`.
- **FR-002**: System MUST establish operational data and model directories: `data/raw/`, `data/processed/`, and `models/ACTIVE/`.
- **FR-003**: System MUST NOT include any top-level generic `src/` directory.
- **FR-004**: System MUST place package initializers (`__init__.py`) or baseline stub files in all room directories to ensure module importability across tracks.
- **FR-005**: System MUST provide an authoritative `plant_config.yaml` at the repository root locking the audited DKASC Site 14 constants (`plant_id: "dka_01"`, `lat: -23.7618`, `lon: 133.8748`, `elevation_m: 545.0`, `tz: "Australia/Darwin"`, `capacity_kwp: 5.4`, `inverter_ac_cap_kw: 5.0`, `tilt_deg: 20.0`, `azimuth_deg: 0.0`, `gamma_per_c: -0.004`, `ref_temp_c: 25.0`, `calibration_factor: 0.92`, `night_threshold_kw: 0.1`).
- **FR-006**: System MUST implement an immutable (`frozen=True`) dataclass `PlantConfig` in `packages/solar_core/config.py`.
- **FR-007**: System MUST implement a pure function `load_plant_config(path: Union[str, Path]) -> PlantConfig` in `packages/solar_core/config.py` that reads YAML and instantiates `PlantConfig`.
- **FR-008**: Validation within `load_plant_config` MUST enforce physical boundaries:
  - `capacity_kwp > inverter_ac_cap_kw > 0.0`
  - `0.0 <= tilt_deg <= 90.0`
  - `0.0 < calibration_factor <= 1.5`
  - `gamma_per_c < 0.0`
  - `lat` within `[-90.0, 90.0]`, `lon` within `[-180.0, 180.0]`
  - `night_threshold_kw > 0.0`
- **FR-009**: Validation within `load_plant_config` MUST raise `ValueError` whenever any parameter violates physical bounds or required fields are missing.
- **FR-010**: All functions in `packages/solar_core/config.py` MUST be 100% pure functions: zero database calls, zero network/HTTP requests, zero system clock queries (`datetime.now()` forbidden).
- **FR-011**: System MUST establish `requirements.txt` at the repository root locking versions for all core dependencies without version conflicts.
- **FR-012**: System MUST verify the existence of the OpenAPI contract at `docs/openapi.json` and ensure it documents the 8 analytical API endpoints.

### Key Entities *(include if feature involves data)*

- **PlantConfig**: Immutable dataclass containing static plant specifications: `plant_id` (str), `lat` (float), `lon` (float), `elevation_m` (float), `tz` (str), `capacity_kwp` (float), `inverter_ac_cap_kw` (float), `tilt_deg` (float), `azimuth_deg` (float), `gamma_per_c` (float), `ref_temp_c` (float), `calibration_factor` (float), `night_threshold_kw` (float).
- **DirectorySkeleton**: The physical 8-room monorepo directory tree with isolated subpackages, operational data paths, and model storage targets.
- **APIContractArtifact**: The OpenAPI 3.0 JSON specification (`docs/openapi.json`) defining the contract between Room 6 (`api/`) and Room 7 (`ui/`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the 8 canonical rooms and 3 operational directories exist with proper packaging stubs and zero presence of generic `src/`.
- **SC-002**: 100% of unit tests verifying `PlantConfig` immutability and `load_plant_config` physical boundary validation pass without failure.
- **SC-003**: Attempted mutation of any `PlantConfig` property raises `FrozenInstanceError` in 100% of test scenarios.
- **SC-004**: Parsing invalid physical parameters (negative capacity, inverter rating $\ge$ capacity, out-of-range tilt, zero or excessive calibration factor) raises `ValueError` in 100% of test cases.
- **SC-005**: `requirements.txt` installs cleanly and `docs/openapi.json` parses as valid OpenAPI 3.0 JSON covering all 8 specified endpoints.

## Assumptions

- Python 3.11+ is used across the host and virtual environments.
- PyYAML is available or specified in `requirements.txt` for parsing configuration files.
- DKASC Site 14 empirical constants have been audited and remain fixed for the `dka_01` plant deployment.
- The contract file `docs/openapi.json` defines the mock-first contract specified in `SG_Master_Spec.md` for the 8 analytical endpoints.
