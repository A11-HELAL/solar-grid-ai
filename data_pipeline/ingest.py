"""DKASC telemetry and Open-Meteo weather data ingestion stub."""

from pathlib import Path
from typing import Optional
import pandas as pd


def ingest_raw_dka(csv_path: Path) -> pd.DataFrame:
    """Ingest raw DKASC 5-minute CSV data stream."""
    raise NotImplementedError("data_pipeline.ingest.ingest_raw_dka is a stub")
