# Phase 0 Research: Foundational Solar Core Configuration & Packaging

**Feature**: `001-solar-core-config`
**Date**: 2026-10-26

## Research Topics & Decisions

### 1. Immutability Strategy for Domain Configuration

- **Decision**: Use standard library `@dataclass(frozen=True, slots=True)` for all configuration entities (`PlantConfig`, `SoilingConfig`, `ValidatorConfig`).
- **Rationale**:
  - `frozen=True` provides strict runtime immutability; attempting to mutate an attribute raises `FrozenInstanceError`.
  - `slots=True` significantly optimizes memory footprint and reduces attribute lookup overhead on low-resource hardware (Core i5-7200U, 8GB RAM).
  - Uses zero external dependencies, maintaining the pure standard-library foundation of `solar_core/config.py`.
- **Alternatives Considered**:
  - *Pydantic v2 `BaseModel(frozen=True)`*: High-performance validation, but introduces a large dependency footprint into the foundational core module. Standard library dataclasses with pure validation functions align closer with Principle II (Pure Functional Core).
  - *NamedTuple*: Immutable, but lacks clean default factory semantics, field-level type introspection, and easy `__post_init__` hooks.

---

### 2. Physical Invariant Validation Architecture

- **Decision**: Implement self-contained pure validation logic executed during dataclass `__post_init__` and exposed via pure helper `validate_plant_config(config: PlantConfig) -> None`, combined with file-level parsing in `load_plant_config(path: Union[str, Path]) -> PlantConfig`.
- **Rationale**:
  - Guaranteeing validation in `__post_init__` prevents unphysical instances from being created even if instantiated directly in code without YAML.
  - Exposing validation as pure functions ensures 100% testability with zero side effects.
  - Timezone validation leverages `zoneinfo.ZoneInfo` from the Python standard library, falling back to descriptive `ValueError` if the timezone key is invalid.
- **Physical Boundaries**:
  - Latitude: $[-90.0, 90.0]$
  - Longitude: $[-180.0, 180.0]$
  - Elevation: $[-500.0, 9000.0]$ meters
  - Nameplate Capacity ($P_{dc}$): $> 0.0$ kWp
  - Inverter Ceiling ($P_{ac}$): $0.0 < P_{ac} \le P_{dc}$ kW (Alice Springs Site 14: 5.0 kW vs 5.4 kWp)
  - Array Tilt: $[0.0, 90.0]$ degrees
  - Array Azimuth: $[0.0, 360.0]$ degrees
  - Temperature Coefficient ($\gamma$): $[-0.015, -0.0001]$ / °C (strictly negative for crystalline silicon)
  - Reference Cell Temperature: $[0.0, 50.0]$ °C (standard reference $25.0^\circ\text{C}$)
  - Calibration Factor: $[0.5, 1.5]$ (Site 14 empirical calibration $0.92$)
  - Night Clear-Sky Threshold: $> 0.0$ kW (Site 14 threshold $0.1$ kW)
  - Short-Gap Interpolation Limit: $\ge 1$ hour (Site 14 limit $2$ hours)
- **Alternatives Considered**:
  - *Validation only in `load_plant_config`*: Rejected because programmatic direct instantiation could bypass physical checks.
  - *External schema validators (e.g. Cerberus, Marshmallow)*: Rejected due to unnecessary complexity and violation of Pure Core isolation.

---

### 3. Packaging & Modern Build Backend

- **Decision**: Configure `pyproject.toml` using `setuptools.build_meta` (PEP 517 / PEP 518 / PEP 621) with package discovery mapping `solar_core*`.
- **Rationale**:
  - Supported natively by modern `pip` (`pip install -e .`).
  - Completely eliminates legacy `setup.py` / `setup.cfg` boilerplates.
  - Enables root package imports across all development modules (`import solar_core`) without modifying `sys.path`.
  - Windows timezone support is guaranteed by adding conditional dependency `"tzdata; platform_system == 'Windows'"`.
- **Alternatives Considered**:
  - *Flit / Hatchling*: Lightweight, but `setuptools` remains the most universally reliable and zero-overhead backend for editable monorepo installations across constrained environments.
  - *Poetry*: Heavyweight lockfile resolution and isolated virtualenv management exceeds requirements for local single-threaded host.

---

### 4. Canonical Feature Columns & Cryptographic Contract

- **Decision**: Formalize `FEATURE_COLUMNS`, `QUALITY_FLAGS`, and `RAW_DKA_SHA256` as top-level immutable tuples and string constants in `solar_core/config.py`.
- **Rationale**:
  - `FEATURE_COLUMNS`: Pinned ordered tuple of 12 model features (`poa_wm2`, `temp_air_c`, `wind_ms`, `temp_module_c`, `clear_sky_kw`, `cloud_cover`, `zenith_deg`, `azimuth_deg`, `hour`, `day_of_year`, `power_kw_lag_1h`, `power_kw_lag_24h`).
  - `QUALITY_FLAGS`: Pinned 5 canonical states `("ok", "interpolated", "missing", "fault_suspect", "out_of_range")`.
  - `RAW_DKA_SHA256`: Pinned hash `"eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0"`.
- **Alternatives Considered**:
  - *Dynamic feature discovery*: Rejected to preserve Metamorphic testing reproducibility and prevent silent input drift.
