# Module Interface Contract: `solar_core.physics`

**Feature**: `002-solar-core-physics`  
**Date**: 2026-10-29 (Updated: 2026-11-18)  
**Location**: `packages/solar_core/physics.py`

## 1. Public API Signatures

```python
"""
Solar-Grid AI: Pure Physics Engine Module (Room 2)
Located at: packages/solar_core/physics.py
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
        DataFrame with columns: apparent_zenith, zenith, apparent_elevation, elevation, azimuth.
        
    Raises
    ------
    ValueError
        If times is not timezone-aware or empty.
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
        POA global irradiance in W/m^2 with name 'poa_clear_sky'. Clamped to 0.0 at night.
        
    Raises
    ------
    ValueError
        If times is not timezone-aware.
    """
    ...

def calculate_faiman_cell_temperature(
    poa_wm2: pd.Series,
    temp_air_c: pd.Series,
    wind_speed_ms: Optional[pd.Series] = None,
    u0: float = 25.0,
    u1: float = 6.84,
) -> pd.Series:
    """Calculate PV cell/module temperature using the empirical Faiman model.
    
    Parameters
    ----------
    poa_wm2 : pd.Series
        Plane-of-array irradiance in W/m^2. Must be non-negative.
    temp_air_c : pd.Series
        Ambient air temperature in deg C.
    wind_speed_ms : Optional[pd.Series], default None
        Wind speed at 10m height in m/s. If None, defaults to a deterministic
        0.0 m/s Series aligned to poa_wm2.index.
    u0 : float, default 25.0
        Combined heat loss factor coefficient in W/(m^2 * C). Must be > 0.
    u1 : float, default 6.84
        Combined heat loss factor wind speed coefficient in W/(m^2 * C * (m/s)). Must be > 0.
        
    Returns
    -------
    pd.Series
        Module/cell temperature in deg C with name 'temp_cell_c'.
        
    Raises
    ------
    ValueError
        If poa_wm2, temp_air_c, or wind_speed_ms contain NaN or Inf values.
        If poa_wm2 contains negative values.
        If wind_speed_ms contains negative values.
        If u0 <= 0 or u1 <= 0.
        If series indices do not match.
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
        gamma_per_c, ref_temp_c, inverter_ac_cap_kw.
    cell_temp_c : Optional[pd.Series], optional
        PV cell/module temperature in deg C. If None, thermal derating is 1.0.
        
    Returns
    -------
    pd.Series
        Calibrated clear-sky power in kW with name 'clear_sky_power_kw',
        clipped to config.inverter_ac_cap_kw (5.0 kW) and clamped to 0.0 at night.
        
    Raises
    ------
    ValueError
        If times is not timezone-aware.
    """
    ...

def is_night(
    clear_sky_power_kw: pd.Series,
    threshold_kw: float = 0.1,
    apparent_zenith_deg: Optional[pd.Series] = None,
) -> pd.Series:
    """Classify daytime vs nighttime based on clear-sky power threshold and solar zenith.
    
    Parameters
    ----------
    clear_sky_power_kw : pd.Series
        Calculated or measured clear-sky power in kW.
    threshold_kw : float, default 0.1
        Power threshold below which is_night is True (Engineering Decision #1, config.night_threshold_kw).
    apparent_zenith_deg : Optional[pd.Series], default None
        Apparent solar zenith angle in degrees. When provided, any timestamp with
        apparent_zenith_deg >= 90.0 is also classified as night.
        
    Returns
    -------
    pd.Series
        Boolean Series where True indicates nighttime / sub-threshold condition:
        (clear_sky_power_kw < threshold_kw) | (apparent_zenith_deg >= 90.0) when apparent_zenith_deg is provided,
        or (clear_sky_power_kw < threshold_kw) otherwise.
    """
    ...
```

---

## 2. Package Exports in `packages/solar_core/__init__.py`

`packages/solar_core/__init__.py` extends its public exports to include:
```python
from .physics import (
    calculate_solar_position,
    calculate_clear_sky_poa,
    calculate_faiman_cell_temperature,
    calculate_clear_sky_power,
    is_night,
)
```
and appends these symbols to `__all__`.

---

## 3. Backward Compatibility Aliases in `packages/solar_core/physics.py`

To support existing code, tests, and walking-skeleton stubs without breaking changes, `packages/solar_core/physics.py` retains thin wrapper aliases:
- `compute_solar_position(timestamps_utc: pd.DatetimeIndex, lat: float, lon: float, elevation_m: float) -> pd.DataFrame`: Thin wrapper delegating to `calculate_solar_position`.
- `compute_clear_sky_power(...) -> pd.Series`: Thin wrapper delegating to `calculate_clear_sky_power`.
