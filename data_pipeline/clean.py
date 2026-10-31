"""Timezone shifting (-9.5h to UTC), resampling, and quality flagging stub."""

from typing import Tuple
import pandas as pd


def clean_and_resample_hourly(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Shift Darwin timestamps to UTC and resample hourly (closed='right', label='right')."""
    raise NotImplementedError("data_pipeline.clean.clean_and_resample_hourly is a stub")
