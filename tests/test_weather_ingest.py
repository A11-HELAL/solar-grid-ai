"""Tests for Open-Meteo weather ingestion (Room 1)."""

from pathlib import Path

import pandas as pd
import pytest

from data_pipeline.ingest import (
    DEFAULT_WEATHER_CSV_PATH,
    WEATHER_COLUMNS,
    ingest_open_meteo,
)


REPO_ROOT = Path(__file__).resolve().parent.parent

VALID_CSV = """ts_utc,ghi_wm2,dni_wm2,dhi_wm2,temp_ambient_c,wind_speed_ms,cloud_cover_pct
2023-01-01 02:00:00+00:00,828.0,614.7,261.0,36.0,6.48,100
2023-01-01 00:00:00+00:00,622.0,761.1,130.0,29.8,2.06,100
2023-01-01 01:00:00+00:00,724.0,618.8,225.0,33.6,3.92,100
"""


def write_csv(tmp_path: Path, content: str) -> Path:
    """Write CSV content to a temporary file and return its path."""
    csv_path = tmp_path / "weather.csv"
    csv_path.write_text(content, encoding="utf-8")
    return csv_path


def test_load_real_weather_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the real Open-Meteo CSV loads via the default path and meets the contract."""
    csv_path = REPO_ROOT / DEFAULT_WEATHER_CSV_PATH
    assert csv_path.exists(), f"Missing real weather file: {csv_path}"

    monkeypatch.chdir(REPO_ROOT)
    weather_df = ingest_open_meteo()

    assert isinstance(weather_df, pd.DataFrame)
    assert not weather_df.empty
    assert tuple(weather_df.columns) == WEATHER_COLUMNS
    assert isinstance(weather_df["ts_utc"].dtype, pd.DatetimeTZDtype)
    assert str(weather_df["ts_utc"].dt.tz) == "UTC"
    assert not weather_df.isna().any().any()
    assert weather_df["ts_utc"].is_monotonic_increasing


@pytest.mark.parametrize(
    "content",
    [
        VALID_CSV.replace(",cloud_cover_pct", ""),
        VALID_CSV.replace("cloud_cover_pct\n", "cloud_cover_pct,extra_col\n").replace(
            ",100\n", ",100,1\n"
        ),
    ],
    ids=["missing_column", "extra_column"],
)
def test_malformed_weather_columns_are_rejected(tmp_path: Path, content: str) -> None:
    """Verify any deviation from the exact column contract raises ValueError."""
    with pytest.raises(ValueError, match="columns must be exactly"):
        ingest_open_meteo(write_csv(tmp_path, content))


def test_rejects_nan_values(tmp_path: Path) -> None:
    """Verify any NaN value raises ValueError."""
    content = VALID_CSV.replace("622.0", "")
    with pytest.raises(ValueError, match="NaN values"):
        ingest_open_meteo(write_csv(tmp_path, content))


def test_rejects_missing_file(tmp_path: Path) -> None:
    """Verify a nonexistent CSV path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        ingest_open_meteo(tmp_path / "does_not_exist.csv")


def test_parses_utc_and_sorts_timestamps(tmp_path: Path) -> None:
    """Verify timestamps are parsed to UTC and rows are sorted ascending."""
    weather_df = ingest_open_meteo(write_csv(tmp_path, VALID_CSV))

    assert tuple(weather_df.columns) == WEATHER_COLUMNS
    assert isinstance(weather_df["ts_utc"].dtype, pd.DatetimeTZDtype)
    assert str(weather_df["ts_utc"].dt.tz) == "UTC"
    assert weather_df["ts_utc"].is_monotonic_increasing
    assert weather_df["ts_utc"].dt.hour.tolist() == [0, 1, 2]
    assert weather_df["ghi_wm2"].tolist() == [622.0, 724.0, 828.0]
