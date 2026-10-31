"""Pure physics functions: solar position, clear-sky irradiance, and thermal derating."""

from typing import Tuple
import pandas as pd


def compute_solar_position(
    timestamps_utc: pd.DatetimeIndex,
    lat: float,
    lon: float,
    elevation_m: float,
) -> pd.DataFrame:
    """Calculate solar azimuth and zenith angle."""
    raise NotImplementedError("solar_core.physics.compute_solar_position is a stub")


def compute_clear_sky_power(
    solar_position: pd.DataFrame,
    capacity_kwp: float,
    tilt_deg: float,
    azimuth_deg: float,
    gamma_per_c: float,
    calibration_factor: float,
) -> pd.Series:
    """Calculate modeled clear-sky power."""
    raise NotImplementedError("solar_core.physics.compute_clear_sky_power is a stub")
