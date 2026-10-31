"""Pure feature engineering and lag transformations for ML training and serving."""

import pandas as pd


def extract_features(telemetry_df: pd.DataFrame) -> pd.DataFrame:
    """Extract standard model features from clean hourly telemetry."""
    raise NotImplementedError("solar_core.features.extract_features is a stub")
