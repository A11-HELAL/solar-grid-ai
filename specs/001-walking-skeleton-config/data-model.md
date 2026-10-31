# Data Model: Foundational Walking Skeleton & Room 2 Configuration Module

## 1. Core Entity: `PlantConfig`

`PlantConfig` is an immutable, pure domain dataclass defined in `packages/solar_core/config.py`.

### Dataclass Definition
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PlantConfig:
    plant_id: str = "dka_01"
    lat: float = -23.7618
    lon: float = 133.8748
    elevation_m: float = 545.0
    tz: str = "Australia/Darwin"
    capacity_kwp: float = 5.4
    inverter_ac_cap_kw: float = 5.0
    tilt_deg: float = 20.0
    azimuth_deg: float = 0.0
    gamma_per_c: float = -0.004
    ref_temp_c: float = 25.0
    calibration_factor: float = 0.92
    night_threshold_kw: float = 0.1
```

### Attribute Details & Physical Invariants

| Field | Type | Default | Physical Invariant / Bounds | Validation Rule |
| :--- | :--- | :--- | :--- | :--- |
| `plant_id` | `str` | `"dka_01"` | Non-empty alphanumeric string | `len(plant_id) > 0` |
| `lat` | `float` | `-23.7618` | WGS84 latitude [-90.0, 90.0] | `-90.0 <= lat <= 90.0` |
| `lon` | `float` | `133.8748` | WGS84 longitude [-180.0, 180.0] | `-180.0 <= lon <= 180.0` |
| `elevation_m` | `float` | `545.0` | Meters above sea level | `elevation_m >= -500.0` |
| `tz` | `str` | `"Australia/Darwin"` | Valid IANA timezone | Must be valid in `zoneinfo.ZoneInfo` |
| `capacity_kwp` | `float` | `5.4` | DC array nameplate capacity | `capacity_kwp > 0.0` |
| `inverter_ac_cap_kw`| `float` | `5.0` | Rated AC inverter ceiling | `0.0 < inverter_ac_cap_kw < capacity_kwp` |
| `tilt_deg` | `float` | `20.0` | Array tilt angle relative to ground | `0.0 <= tilt_deg <= 90.0` |
| `azimuth_deg` | `float` | `0.0` | True azimuth angle (0.0 = True North) | `0.0 <= azimuth_deg < 360.0` |
| `gamma_per_c` | `float` | `-0.004` | Power temp coefficient (-0.4%/°C) | `gamma_per_c < 0.0` |
| `ref_temp_c` | `float` | `25.0` | Standard test condition cell temp | `ref_temp_c > 0.0` |
| `calibration_factor`| `float` | `0.92` | Historical empirical clear-sky factor | `0.0 < calibration_factor <= 1.5` |
| `night_threshold_kw`| `float` | `0.1` | Night boundary clear-sky threshold | `night_threshold_kw > 0.0` |

### Immutability & Lifecycle
- `frozen=True`: Any in-place modification (e.g., `config.capacity_kwp = 10.0`) raises `dataclasses.FrozenInstanceError`.
- Pure instantiation: Direct instantiation is supported for fast unit tests without disk access.
- File loading: Instantiation from YAML executes through pure function `load_plant_config(path: Union[str, Path]) -> PlantConfig` with validation.

---

## 2. Structural Entity: 8-Room Directory Layout

```text
/ (Repository Root)
├── plant_config.yaml                  # Authoritative DKASC Site 14 constants
├── requirements.txt                   # Locked environment dependencies
├── pyproject.toml                     # Solar core package installer
├── docs/
│   ├── SG_Master_Spec.md              # Architectural master specification
│   ├── SG_Data_Spec.md                # Data engineering specification
│   └── openapi.json                   # OpenAPI 3.0 contract for 8 analytical endpoints
├── data/
│   ├── raw/                           # Raw telemetry storage (.gitkeep)
│   └── processed/                     # Resampled clean parquet/CSV (.gitkeep)
├── models/
│   └── ACTIVE/                        # Production model artifacts (.gitkeep)
├── data_pipeline/                     # Room 1: Telemetry ingestion & transformation
│   ├── __init__.py
│   ├── ingest.py                      # Data ingestion stub
│   └── clean.py                       # Timezone shifting & cleaning stub
├── packages/
│   └── solar_core/                    # Room 2: Pure physics & domain engine
│       ├── __init__.py                # Package exports (__version__, PlantConfig, load_plant_config)
│       ├── pyproject.toml             # Local package definition
│       ├── config.py                  # PlantConfig dataclass & load_plant_config loader
│       ├── physics.py                 # Pure solar position & clear-sky stub
│       ├── features.py                # Pure feature transformation stub
│       ├── validator.py               # H1-H5 guardrails & health check stub
│       ├── soiling.py                 # Soiling loss model & PR stub
│       └── sim.py                     # Synthetic PV simulation stub
├── ml_training/                       # Room 3: ML training pipeline
│   ├── __init__.py
│   ├── data_loader.py                 # Training dataset loader stub
│   ├── train.py                       # M0-M4 training harness stub
│   ├── evaluate.py                    # Validation & error metric stub
│   └── export.py                      # JSON serialization stub (model.json + metadata.json)
├── db/                                # Room 4: Relational persistence
│   ├── __init__.py
│   └── init/
│       └── 01_schema.sql              # PostgreSQL 16 schema stub
├── worker/                            # Room 5: Scheduled operational jobs
│   ├── __init__.py
│   └── jobs.py                        # replay_job, soiling_job, forecast_job stub
├── api/                               # Room 6: FastAPI analytical service
│   ├── __init__.py
│   └── main.py                        # FastAPI application entry stub
├── ui/                                # Room 7: React + Vite + Recharts frontend
│   ├── package.json                   # UI dependency manifest stub
│   └── src/
│       └── App.tsx                    # UI entry stub
└── tests/                             # Room 8: Test suite & QA Gates
    ├── __init__.py
    ├── conftest.py                    # Pytest configuration & test fixtures
    └── test_config.py                 # Complete unit tests for PlantConfig & load_plant_config
```
