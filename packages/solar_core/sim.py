"""Pure synthetic telemetry and PV anomaly simulation engine."""

import pandas as pd


def generate_synthetic_profile(
    timestamps_utc: pd.DatetimeIndex,
    capacity_kwp: float,
) -> pd.DataFrame:
    """Generate deterministic synthetic solar telemetry for testing."""
    raise NotImplementedError("solar_core.sim.generate_synthetic_profile is a stub")
