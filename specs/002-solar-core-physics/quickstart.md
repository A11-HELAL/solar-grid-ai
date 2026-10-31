# Quickstart: Validating Pure Physics Engine & Golden Solstice Tests

**Feature**: `002-solar-core-physics`
**Date**: 2026-10-29

## Prerequisites

- Python environment with `solar_core` installed (`pip install -e .`)
- Working directory: `e:\Graduation Project\files`

---

## 1. Quick Solar Position & Clear-Sky Calculation

Run a quick interactive Python check:

```bash
python -c "
import pandas as pd
from solar_core.config import PlantConfig
from solar_core.physics import calculate_solar_position, calculate_clear_sky_poa, calculate_clear_sky_power, is_night

config = PlantConfig()
times = pd.date_range('2026-06-21 00:00', '2026-06-21 23:00', freq='1h', tz='UTC')

sol_pos = calculate_solar_position(times, config)
poa = calculate_clear_sky_poa(times, config)
power = calculate_clear_sky_power(times, config)
night = is_night(power)

print('Noon apparent zenith:', sol_pos['apparent_zenith'].min())
print('Max POA irradiance:', poa.max(), 'W/m^2')
print('Max Clear-Sky Power:', power.max(), 'kW')
print('Daytime hours count:', (~night).sum())
assert power.max() > 0.0
assert (power[night] == 0.0).all() or (power[night] < 0.1).all()
"
```

---

## 2. Metamorphic Relation MR4 Property Test

Verify that nighttime power is identically 0.0 kW under arbitrary temperature perturbations:

```bash
python -c "
import pandas as pd
import numpy as np
from solar_core.config import PlantConfig
from solar_core.physics import calculate_clear_sky_power, is_night

config = PlantConfig()
night_times = pd.date_range('2026-06-21 14:00', '2026-06-21 21:00', freq='1h', tz='UTC') # Deep night in Alice Springs

for temp in [-10.0, 0.0, 25.0, 50.0, 75.0]:
    temp_series = pd.Series(temp, index=night_times)
    p_night = calculate_clear_sky_power(night_times, config, cell_temp_c=temp_series)
    assert (p_night == 0.0).all(), f'MR4 violation at temp={temp}'
print('MR4 Property Verified: Nighttime power is identically 0.0 kW across all temperatures.')
"
```

---

## 3. Full Physics Test Suite Execution

Run pytest against the physics test suite:

```bash
pytest tests/test_physics.py -v
```

**Expected Outcome**: 100% of unit, property, and golden tests pass.
