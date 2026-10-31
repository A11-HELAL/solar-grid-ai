"""Shared pytest fixtures and test environment configuration."""

from pathlib import Path
import pytest


@pytest.fixture
def repo_root() -> Path:
    """Return repository root path."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def plant_config_path(repo_root: Path) -> Path:
    """Return path to root plant_config.yaml."""
    return repo_root / "plant_config.yaml"
