"""Training dataset loader with train/val/test temporal splitting."""

from pathlib import Path
from typing import Tuple
import pandas as pd


def load_training_dataset(
    processed_dir: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load cleaned dataset and split temporally into train, val, and test partitions."""
    raise NotImplementedError("ml_training.data_loader.load_training_dataset is a stub")
