# Quickstart: Validating Foundational Solar Core Configuration & Packaging

**Feature**: `001-solar-core-config`
**Date**: 2026-10-26

## Prerequisites

- Python 3.10+ installed
- Virtual environment activated (recommended)
- Working directory set to the repository root: `e:\Graduation Project\files`

---

## 1. Editable Package Installation

From the repository root, install `solar_core` in editable mode:

```bash
pip install -e .
```

**Expected Outcome**: `solar_core` is installed in editable development mode, resolving dependencies (`pyyaml`, `pvlib`, `numpy`, `pandas`, `pydantic`).

---

## 2. Package Entrypoint & Version Verification

Run an interactive Python one-liner to verify top-level package attributes:

```bash
python -c "import solar_core; print(solar_core.CORE_VERSION); assert solar_core.CORE_VERSION == '1.1.0'"
```

**Expected Outcome**: Output prints `1.1.0` and exits with code 0.

---

## 3. Configuration Loading & Physical Realism Verification

Verify loading the root `plant_config.yaml`:

```bash
python -c "
from pathlib import Path
from solar_core.config import load_plant_config, PlantConfig

config = load_plant_config(Path('plant_config.yaml'))
print('Loaded plant:', config.plant_id, 'Capacity:', config.capacity_kwp, 'kWp')
assert isinstance(config, PlantConfig)
assert config.plant_id == 'dka_01'
assert config.capacity_kwp == 5.4
assert config.inverter_kw == 5.0
"
```

**Expected Outcome**: Prints `Loaded plant: dka_01 Capacity: 5.4 kWp` with exit code 0.

---

## 4. Immutability Enforcement Verification

Verify that frozen dataclasses block runtime mutation:

```bash
python -c "
from dataclasses import FrozenInstanceError
from solar_core.config import PlantConfig

config = PlantConfig()
try:
    config.capacity_kwp = 100.0
    raise AssertionError('Mutation succeeded unexpectedly!')
except FrozenInstanceError:
    print('Immutability verified successfully.')
"
```

**Expected Outcome**: Prints `Immutability verified successfully.` with exit code 0.

---

## 5. Physical Invariant Boundary Rejection

Verify that unphysical parameters are immediately rejected:

```bash
python -c "
from solar_core.config import PlantConfig

# Test negative capacity
try:
    PlantConfig(capacity_kwp=-5.0)
    raise AssertionError('Negative capacity was not rejected!')
except ValueError as e:
    print('Validation caught invalid capacity:', e)

# Test positive thermal coefficient
try:
    PlantConfig(gamma_per_c=0.005)
    raise AssertionError('Positive gamma was not rejected!')
except ValueError as e:
    print('Validation caught invalid gamma:', e)
"
```

**Expected Outcome**: Prints both validation error messages and exits with code 0.

---

## 6. Test Suite Execution

Run pytest against unit tests covering all configuration models and boundary conditions:

```bash
pytest tests/unit/test_config.py -v
```

**Expected Outcome**: 100% of unit tests pass.
