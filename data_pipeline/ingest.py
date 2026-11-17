"""DKASC telemetry and Open-Meteo weather data ingestion stub."""

from pathlib import Path
from typing import Optional
import pandas as pd


DEFAULT_WEATHER_CSV_PATH = Path("data/raw/open_meteo_dka_2023_2025.csv")

WEATHER_COLUMNS = (
    "ts_utc",
    "ghi_wm2",
    "dni_wm2",
    "dhi_wm2",
    "temp_ambient_c",
    "wind_speed_ms",
    "cloud_cover_pct",
)


def ingest_open_meteo(csv_path: Path = DEFAULT_WEATHER_CSV_PATH) -> pd.DataFrame:
    """Load and validate hourly Open-Meteo weather data in UTC."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing weather CSV: {csv_path}")

    weather_df = pd.read_csv(csv_path)

    if tuple(weather_df.columns) != WEATHER_COLUMNS:
        raise ValueError(
            f"Weather CSV columns must be exactly {list(WEATHER_COLUMNS)}, "
            f"got {list(weather_df.columns)}"
        )

    weather_df["ts_utc"] = pd.to_datetime(weather_df["ts_utc"], utc=True)

    if weather_df.isna().any().any():
        null_columns = weather_df.columns[weather_df.isna().any()].tolist()
        raise ValueError(f"Weather CSV contains NaN values in columns: {null_columns}")

    weather_df = weather_df.sort_values("ts_utc", kind="stable").reset_index(drop=True)
    return weather_df


def ingest_raw_dka(csv_path: Path) -> pd.DataFrame:
    """Ingest raw DKASC 5-minute CSV data stream."""
    raise NotImplementedError("data_pipeline.ingest.ingest_raw_dka is a stub")
