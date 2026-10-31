"""Pure configuration models and loaders for Solar-Grid AI (Room 2)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Union
import yaml

__all__ = ["PlantConfig", "load_plant_config"]


@dataclass(frozen=True, slots=True)
class PlantConfig:
    """Immutable plant configuration for DKASC Site 14 (dka_01)."""

    plant_id: str = "dka_01"
    lat: float = -23.7618
    lon: float = 133.8748
    elevation_m: float = 545.0
    tz: str = "Australia/Darwin"
    capacity_kwp: float = 5.4
    inverter_ac_cap_kw: float = 5.0
    tilt_deg: float = 20.0
    azimuth_deg: float = 0.0
    gamma_per_c: float = -0.004
    ref_temp_c: float = 25.0
    calibration_factor: float = 0.92
    night_threshold_kw: float = 0.1


def load_plant_config(path: Union[str, Path]) -> PlantConfig:
    """Load, validate, and return immutable PlantConfig from YAML file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        data: Any = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError(f"Malformed YAML in {file_path}: {exc}") from exc

    if not data or not isinstance(data, dict):
        raise ValueError(f"Empty configuration or invalid dictionary mapping in {file_path}")

    required_sections = ["plant", "array", "physics"]
    for section in required_sections:
        if section not in data or not isinstance(data[section], dict):
            raise ValueError(f"Missing required section '{section}' in {file_path}")

    plant_data = data["plant"]
    array_data = data["array"]
    physics_data = data["physics"]

    location_data = plant_data.get("location")
    if not location_data or not isinstance(location_data, dict):
        raise ValueError(f"Missing required 'location' mapping in plant section of {file_path}")

    plant_id = str(plant_data.get("id", ""))
    if not plant_id:
        raise ValueError(f"Missing required plant 'id' in {file_path}")

    lat = float(location_data.get("lat", 0.0))
    lon = float(location_data.get("lon", 0.0))
    elevation_m = float(location_data.get("elevation_m", 0.0))
    tz = str(location_data.get("tz", ""))

    capacity_kwp = float(array_data.get("capacity_kwp", 0.0))
    inverter_ac_cap_kw = float(array_data.get("inverter_ac_cap_kw", 0.0))
    tilt_deg = float(array_data.get("tilt_deg", 0.0))
    azimuth_deg = float(array_data.get("azimuth_deg", 0.0))

    gamma_per_c = float(physics_data.get("gamma_per_c", 0.0))
    ref_temp_c = float(physics_data.get("ref_temp_c", 25.0))
    calibration_factor = float(physics_data.get("calibration_factor", 0.0))
    night_threshold_kw = float(physics_data.get("night_threshold_kw", 0.0))

    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"lat must be within [-90.0, 90.0], got {lat}")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"lon must be within [-180.0, 180.0], got {lon}")
    if elevation_m < -500.0:
        raise ValueError(f"elevation_m must be >= -500.0, got {elevation_m}")
    if not tz:
        raise ValueError("tz timezone string must not be empty")

    if inverter_ac_cap_kw <= 0.0:
        raise ValueError(f"inverter_ac_cap_kw must be positive, got {inverter_ac_cap_kw}")
    if capacity_kwp <= inverter_ac_cap_kw:
        raise ValueError(
            f"capacity_kwp must be greater than inverter_ac_cap_kw, "
            f"got capacity={capacity_kwp}, inverter={inverter_ac_cap_kw}"
        )
    if not (0.0 <= tilt_deg <= 90.0):
        raise ValueError(f"tilt_deg must be within [0.0, 90.0], got {tilt_deg}")
    if not (0.0 <= azimuth_deg < 360.0):
        raise ValueError(f"azimuth_deg must be within [0.0, 360.0), got {azimuth_deg}")

    if gamma_per_c >= 0.0:
        raise ValueError(f"gamma_per_c must be negative, got {gamma_per_c}")
    if not (0.0 < calibration_factor <= 1.5):
        raise ValueError(f"calibration_factor must be within (0.0, 1.5], got {calibration_factor}")
    if night_threshold_kw <= 0.0:
        raise ValueError(f"night_threshold_kw must be positive, got {night_threshold_kw}")

    return PlantConfig(
        plant_id=plant_id,
        lat=lat,
        lon=lon,
        elevation_m=elevation_m,
        tz=tz,
        capacity_kwp=capacity_kwp,
        inverter_ac_cap_kw=inverter_ac_cap_kw,
        tilt_deg=tilt_deg,
        azimuth_deg=azimuth_deg,
        gamma_per_c=gamma_per_c,
        ref_temp_c=ref_temp_c,
        calibration_factor=calibration_factor,
        night_threshold_kw=night_threshold_kw,
    )
