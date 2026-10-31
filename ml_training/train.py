"""Model training routines for baseline (M0) through Clear-Sky Ratio XGBoost (M4)."""

from typing import Any, Dict
import pandas as pd


def train_xgboost_ratio_model(
    train_df: pd.DataFrame,
    hyperparameters: Dict[str, Any],
) -> Any:
    """Train XGBoost model to predict clear-sky ratio r with monotone constraints."""
    raise NotImplementedError("ml_training.train.train_xgboost_ratio_model is a stub")
