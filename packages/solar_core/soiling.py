"""Pure soiling derating estimation and performance ratio tracking."""

from typing import Tuple
import pandas as pd


def compute_daily_pr_tc(
    hourly_df: pd.DataFrame,
    inverter_ceiling_kw: float = 4.95,
    min_poa_wm2: float = 500.0,
) -> pd.DataFrame:
    """Calculate daily temperature-corrected PR filtering out clipped hours."""
    raise NotImplementedError("solar_core.soiling.compute_daily_pr_tc is a stub")
