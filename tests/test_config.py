"""Unit tests for PlantConfig dataclass and load_plant_config function (Room 2)."""

from dataclasses import FrozenInstanceError
from pathlib import Path
import pytest

from solar_core.config import PlantConfig, load_plant_config


VALID_YAML_CONTENT = """
plant:
  id: "dka_01"
  name: "DKA Solar Centre Site 14"
  location:
    lat: -23.7618
    lon: 133.8748
    elevation_m: 545.0
    tz: "Australia/Darwin"

array:
  capacity_kwp: 5.4
  inverter_ac_cap_kw: 5.0
  tilt_deg: 20.0
  azimuth_deg: 0.0

physics:
  gamma_per_c: -0.004
  ref_temp_c: 25.0
  calibration_factor: 0.92
  night_threshold_kw: 0.1
"""


def test_plant_config_defaults() -> None:
    """Verify default values match DKASC Site 14 constants."""
    config = PlantConfig()
    assert config.plant_id == "dka_01"
    assert config.lat == -23.7618
    assert config.lon == 133.8748
    assert config.elevation_m == 545.0
    assert config.tz == "Australia/Darwin"
    assert config.capacity_kwp == 5.4
    assert config.inverter_ac_cap_kw == 5.0
    assert config.tilt_deg == 20.0
    assert config.azimuth_deg == 0.0
    assert config.gamma_per_c == -0.004
    assert config.ref_temp_c == 25.0
    assert config.calibration_factor == 0.92
    assert config.night_threshold_kw == 0.1


def test_plant_config_immutability() -> None:
    """Verify PlantConfig attributes cannot be modified post-instantiation."""
    config = PlantConfig()
    with pytest.raises(FrozenInstanceError):
        config.capacity_kwp = 10.0  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        config.plant_id = "other_plant"  # type: ignore[misc]


def test_load_plant_config_valid(tmp_path: Path) -> None:
    """Verify valid YAML file is parsed into a PlantConfig instance."""
    yaml_file = tmp_path / "valid_config.yaml"
    yaml_file.write_text(VALID_YAML_CONTENT, encoding="utf-8")

    config = load_plant_config(yaml_file)
    assert isinstance(config, PlantConfig)
    assert config.plant_id == "dka_01"
    assert config.capacity_kwp == 5.4
    assert config.inverter_ac_cap_kw == 5.0
    assert config.calibration_factor == 0.92


def test_load_plant_config_missing_file(tmp_path: Path) -> None:
    """Verify FileNotFoundError is raised when file does not exist."""
    missing_path = tmp_path / "non_existent_file.yaml"
    with pytest.raises(FileNotFoundError):
        load_plant_config(missing_path)


def test_load_plant_config_malformed_yaml(tmp_path: Path) -> None:
    """Verify ValueError is raised on malformed YAML syntax."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("plant: [unclosed list", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed YAML"):
        load_plant_config(bad_yaml)


def test_load_plant_config_empty_file(tmp_path: Path) -> None:
    """Verify ValueError is raised on empty configuration file."""
    empty_yaml = tmp_path / "empty.yaml"
    empty_yaml.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Empty configuration"):
        load_plant_config(empty_yaml)


def test_load_plant_config_missing_required_keys(tmp_path: Path) -> None:
    """Verify ValueError is raised when required root sections are missing."""
    incomplete_yaml = tmp_path / "incomplete.yaml"
    incomplete_yaml.write_text("plant:\n  id: 'dka_01'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required section"):
        load_plant_config(incomplete_yaml)


def test_load_plant_config_inverter_exceeds_capacity(tmp_path: Path) -> None:
    """Verify ValueError when inverter capacity equals or exceeds array capacity."""
    invalid_yaml = VALID_YAML_CONTENT.replace("inverter_ac_cap_kw: 5.0", "inverter_ac_cap_kw: 6.0")
    cfg_file = tmp_path / "invalid.yaml"
    cfg_file.write_text(invalid_yaml, encoding="utf-8")
    with pytest.raises(ValueError, match="capacity_kwp must be greater than inverter_ac_cap_kw"):
        load_plant_config(cfg_file)


def test_load_plant_config_inverter_non_positive(tmp_path: Path) -> None:
    """Verify ValueError when inverter capacity is <= 0."""
    invalid_yaml = VALID_YAML_CONTENT.replace("inverter_ac_cap_kw: 5.0", "inverter_ac_cap_kw: 0.0")
    cfg_file = tmp_path / "invalid.yaml"
    cfg_file.write_text(invalid_yaml, encoding="utf-8")
    with pytest.raises(ValueError, match="inverter_ac_cap_kw must be positive"):
        load_plant_config(cfg_file)


def test_load_plant_config_positive_gamma(tmp_path: Path) -> None:
    """Verify ValueError when temperature coefficient gamma is non-negative."""
    invalid_yaml = VALID_YAML_CONTENT.replace("gamma_per_c: -0.004", "gamma_per_c: 0.004")
    cfg_file = tmp_path / "invalid.yaml"
    cfg_file.write_text(invalid_yaml, encoding="utf-8")
    with pytest.raises(ValueError, match="gamma_per_c must be negative"):
        load_plant_config(cfg_file)


def test_load_plant_config_negative_tilt(tmp_path: Path) -> None:
    """Verify ValueError when tilt is negative."""
    invalid_yaml = VALID_YAML_CONTENT.replace("tilt_deg: 20.0", "tilt_deg: -5.0")
    cfg_file = tmp_path / "invalid.yaml"
    cfg_file.write_text(invalid_yaml, encoding="utf-8")
    with pytest.raises(ValueError, match="tilt_deg must be within"):
        load_plant_config(cfg_file)


def test_load_plant_config_tilt_exceeds_90(tmp_path: Path) -> None:
    """Verify ValueError when tilt exceeds 90 degrees."""
    invalid_yaml = VALID_YAML_CONTENT.replace("tilt_deg: 20.0", "tilt_deg: 95.0")
    cfg_file = tmp_path / "invalid.yaml"
    cfg_file.write_text(invalid_yaml, encoding="utf-8")
    with pytest.raises(ValueError, match="tilt_deg must be within"):
        load_plant_config(cfg_file)


def test_load_plant_config_calibration_factor_out_of_bounds(tmp_path: Path) -> None:
    """Verify ValueError when calibration_factor is outside (0, 1.5]."""
    invalid_zero = VALID_YAML_CONTENT.replace("calibration_factor: 0.92", "calibration_factor: 0.0")
    file_zero = tmp_path / "zero.yaml"
    file_zero.write_text(invalid_zero, encoding="utf-8")
    with pytest.raises(ValueError, match="calibration_factor must be within"):
        load_plant_config(file_zero)

    invalid_high = VALID_YAML_CONTENT.replace("calibration_factor: 0.92", "calibration_factor: 1.8")
    file_high = tmp_path / "high.yaml"
    file_high.write_text(invalid_high, encoding="utf-8")
    with pytest.raises(ValueError, match="calibration_factor must be within"):
        load_plant_config(file_high)


def test_load_plant_config_invalid_coordinates(tmp_path: Path) -> None:
    """Verify ValueError when coordinates violate WGS84 bounds."""
    invalid_lat = VALID_YAML_CONTENT.replace("lat: -23.7618", "lat: 95.0")
    file_lat = tmp_path / "lat.yaml"
    file_lat.write_text(invalid_lat, encoding="utf-8")
    with pytest.raises(ValueError, match="lat must be within"):
        load_plant_config(file_lat)


def test_load_root_plant_config(plant_config_path: Path) -> None:
    """Verify repository root plant_config.yaml loads cleanly and matches Site 14 constants."""
    assert plant_config_path.exists(), f"Missing root configuration file: {plant_config_path}"
    config = load_plant_config(plant_config_path)

    assert config.plant_id == "dka_01"
    assert config.lat == -23.7618
    assert config.lon == 133.8748
    assert config.elevation_m == 545.0
    assert config.tz == "Australia/Darwin"
    assert config.capacity_kwp == 5.4
    assert config.inverter_ac_cap_kw == 5.0
    assert config.tilt_deg == 20.0
    assert config.azimuth_deg == 0.0
    assert config.gamma_per_c == -0.004
    assert config.ref_temp_c == 25.0
    assert config.calibration_factor == 0.92
    assert config.night_threshold_kw == 0.1
