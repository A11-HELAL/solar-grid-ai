# Architectural Research: Foundational Walking Skeleton & Room 2 Configuration Module

## Decision 1: Configuration Representation
- **Decision**: Standard library `dataclasses.dataclass(frozen=True, slots=True)` for `PlantConfig`.
- **Rationale**:
  - Provides guaranteed immutability via `FrozenInstanceError` on any attempted attribute modification.
  - Zero third-party runtime dependency within `packages/solar_core/config.py` (pure standard library).
  - Minimal memory overhead (~60 bytes per instance) and sub-microsecond instantiation time, perfectly aligning with host hardware constraints (Core i5-7200U, 8GB RAM).
- **Alternatives Considered**:
  - `pydantic.BaseModel`: Feature-rich but introduces heavier startup overhead and external dependency on Pydantic v2 within core physics.
  - `typing.NamedTuple`: Immutable and lightweight, but lacks clear dataclass default representations and clean docstring metadata.

## Decision 2: YAML Loading & Strict Physical Boundary Validation
- **Decision**: `yaml.safe_load` wrapped inside a pure function `load_plant_config(path: Union[str, Path]) -> PlantConfig` with explicit physical boundary guards.
- **Rationale**:
  - `yaml.safe_load` prevents arbitrary Python object deserialization vulnerabilities.
  - Pure validation logic ensures all physical parameters (`capacity_kwp > inverter_ac_cap_kw > 0`, `tilt in [0, 90]`, `calibration_factor in (0, 1.5]`, `gamma < 0`, `night_threshold_kw > 0`) are validated deterministically before returning the frozen instance.
  - Explicit error handling raises `FileNotFoundError` for missing paths and `ValueError` with clear, actionable messages for malformed YAML or out-of-bound physics values.
- **Alternatives Considered**:
  - Validating in `__post_init__` of `PlantConfig`: Possible, but separating file I/O and validation into `load_plant_config` keeps `PlantConfig` directly instantiable in pure unit tests while ensuring files are validated upon ingestion.

## Decision 3: 8-Room Layout & Monorepo Import Resolution
- **Decision**: Establish the 8 canonical rooms (`data_pipeline/`, `packages/solar_core/`, `ml_training/`, `db/`, `worker/`, `api/`, `ui/`, `tests/`) alongside operational directories (`data/raw/`, `data/processed/`, `models/ACTIVE/`). Provide `pyproject.toml` targeting `packages/solar_core` for editable installation (`pip install -e packages/solar_core`).
- **Rationale**:
  - Strictly enforces Constitution Principle I: bans generic `src/` directory.
  - Guarantees seamless imports (`from solar_core.config import PlantConfig, load_plant_config`) across all rooms, CI test runners, and developer environments.
  - Initializes empty `__init__.py` and module stubs so team tracks can develop concurrently without import errors.
- **Alternatives Considered**:
  - Modifying `sys.path` dynamically in test files: Fragile, non-standard, and causes linting/typing failures in IDEs.

## Decision 4: Contract-First API Baseline (`docs/openapi.json`)
- **Decision**: Establish a complete OpenAPI 3.0 specification artifact at `docs/openapi.json` defining the 8 analytical endpoints.
- **Rationale**:
  - Room 6 (`api/`) and Room 7 (`ui/`) require a shared, authoritative schema contract before writing endpoint implementations or React dashboards.
  - Enables mock-first client generation (`MOCK=1`) and automated contract tests in Room 8 (`tests/`).
- **Alternatives Considered**:
  - Auto-generating `openapi.json` from FastAPI at runtime: Violates contract-first design; frontend developers would be blocked until the FastAPI backend is implemented.
