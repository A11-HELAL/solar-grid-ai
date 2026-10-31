# Module Interface Contract: `solar_core` & `solar_core.config`

**Feature**: `001-solar-core-config`
**Date**: 2026-10-26

## 1. Package Exports (`solar_core/__init__.py`)

The package entry point MUST expose the version string and primary symbols:

```python
"""
Solar-Grid AI: Pure Functional Solar Core
"""

from solar_core.config import (
    CORE_VERSION,
    FEATURE_COLUMNS,
    QUALITY_FLAGS,
    RAW_DKA_SHA256,
    PlantConfig,
    SoilingConfig,
    ValidatorConfig,
    load_plant_config,
    validate_plant_config,
)

__all__ = [
    "CORE_VERSION",
    "PlantConfig",
    "SoilingConfig",
    "ValidatorConfig",
    "load_plant_config",
    "validate_plant_config",
    "QUALITY_FLAGS",
    "RAW_DKA_SHA256",
    "FEATURE_COLUMNS",
]

__version__ = CORE_VERSION
```

- `CORE_VERSION: str = "1.1.0"`

---

## 2. Configuration Module Public API (`solar_core/config.py`)

### Functions

#### `validate_plant_config(config: PlantConfig) -> None`
- **Description**: Validates that all attributes of a `PlantConfig` instance satisfy physical and operational realism bounds.
- **Parameters**: `config` (`PlantConfig`) — The instance to validate.
- **Returns**: `None`
- **Raises**: `ValueError` — When any parameter violates physical reality (e.g. out-of-range coordinates, inverted temperature coefficient, inverter capacity exceeding DC array).

#### `load_plant_config(path: Union[str, Path]) -> PlantConfig`
- **Description**: Loads a YAML file from disk, verifies structure and mandatory keys, and instantiates an immutable, physically validated `PlantConfig`.
- **Parameters**: `path` (`Union[str, Path]`) — File path to the plant configuration YAML.
- **Returns**: `PlantConfig` — The validated, immutable configuration object.
- **Raises**:
  - `FileNotFoundError` — If the file does not exist at `path`.
  - `ValueError` — If the YAML content is malformed, not a mapping/dictionary, missing required keys, or contains physically invalid values.

---

## 3. Immutability Guarantee

All dataclass instances (`PlantConfig`, `SoilingConfig`, `ValidatorConfig`) MUST be decorated with `@dataclass(frozen=True, slots=True)`:
```python
>>> config = PlantConfig()
>>> config.capacity_kwp = 10.0
Traceback (most recent call last):
    ...
dataclasses.FrozenInstanceError: cannot assign to field 'capacity_kwp'
```
