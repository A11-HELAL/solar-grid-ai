"""Validation tests for monorepo 8-room layout and absence of generic src/ directory."""

from pathlib import Path


def test_no_generic_src_directory(repo_root: Path) -> None:
    """Ensure top-level generic src/ directory does not exist."""
    src_dir = repo_root / "src"
    assert not src_dir.exists(), "Constitution Violation: generic src/ directory found at root"


def test_eight_rooms_exist(repo_root: Path) -> None:
    """Ensure all 8 canonical rooms exist with package initializers or stubs."""
    required_rooms = [
        "data_pipeline",
        "packages/solar_core",
        "ml_training",
        "db",
        "worker",
        "api",
        "ui",
        "tests",
    ]
    for room in required_rooms:
        room_path = repo_root / room
        assert room_path.is_dir(), f"Missing architectural room: {room}"


def test_operational_directories_exist(repo_root: Path) -> None:
    """Ensure operational data and model directories exist."""
    operational_dirs = [
        "data/raw",
        "data/processed",
        "models/ACTIVE",
    ]
    for op_dir in operational_dirs:
        op_path = repo_root / op_dir
        assert op_path.is_dir(), f"Missing operational directory: {op_dir}"
