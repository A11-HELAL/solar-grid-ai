# Module Interface Contract: `solar_core.physics`

**Feature**: `002-solar-core-physics`
**Date**: 2026-10-29

## 1. Public API Signatures

```python
"""
Solar-Grid AI: Pure Physics Engine Module
"""
from typing import Optional
import pandas as pd
from solar_core.config import PlantConfig

def calculate_solar_position(
    times: pd.DatetimeIndex,
    config: PlantConfig,
) -> pd.DataFrame:
    """Calculate solar position angles for the plant location.
    
    Parameters
    ----------
    times : pd.DatetimeIndex
        Timezone-aware timestamps. Must have valid tz (UTC enforced/converted).
    config : PlantConfig
        Plant configuration containing lat, lon, elevation_m.
        
    Returns
    -------
    pd.DataFrame
        DataFrame with apparent_zenith, zenith, apparent_elevation, elevation, azimuth.
        
    Raises
    ------
    ValueError
        If times is not timezone-aware.
    """
    ...

def calculate_clear_sky_poa(
    times: pd.DatetimeIndex,
    config: PlantConfig,
) -> pd.Series:
    """Calculate transposed plane-of-array clear-sky irradiance (W/m^2).
    
    Parameters
    ----------
    times : pd.DatetimeIndex
        Timezone-aware timestamps.
    config : PlantConfig
        Plant configuration containing site coordinates, tilt_deg, azimuth_deg.
        
    Returns
    -------
    pd.Series
        POA global irradiance in W/m^2. Clamped to 0.0 at night.
        
    Raises
    ------
    ValueError
        If times is not timezone-aware.
    """
    ...

def calculate_clear_sky_power(
    times: pd.DatetimeIndex,
    config: PlantConfig,
    cell_temp_c: Optional[pd.Series] = None,
) -> pd.Series:
    """Calculate calibrated, temperature-derated clear-sky AC power (kW).
    
    Parameters
    ----------
    times : pd.DatetimeIndex
        Timezone-aware timestamps.
    config : PlantConfig
        Plant configuration containing capacity_kwp, calibration_factor,
        gamma_per_c, ref_temp_c, inverter_kw.
    cell_temp_c : Optional[pd.Series], optional
        PV cell/module temperature in deg C. If None, thermal derating is 1.0.
        
    Returns
    -------
    pd.Series
        Calibrated clear-sky power in kW, clipped to inverter_kw and clamped to 0.0 at night.
        
    Raises
    ------
    ValueError
        If times is not timezone-aware.
    """
    ...

def is_night(
    clear_sky_power_kw: pd.Series,
    threshold_kw: float = 0.1,
) -> pd.Series:
    """Classify daytime vs nighttime based on clear-sky power threshold.
    
    Parameters
    ----------
    clear_sky_power_kw : pd.Series
        Calculated or measured clear-sky power in kW.
    threshold_kw : float, default 0.1
        Power threshold below which is_night is True (Engineering Decision #1).
        
    Returns
    -------
    pd.Series
        Boolean Series where True indicates nighttime / sub-threshold condition.
    """
    ...
```

---

## 2. Package Exports in `solar_core/__init__.py`

`solar_core/__init__.py` will extend its exports to include:
```python
from solar_core.physics import (
    calculate_solar_position,
    calculate_clear_sky_poa,
    calculate_clear_sky_power,
    is_night,
)
```
and append these symbols to `__all__`.
