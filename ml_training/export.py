"""Portable JSON serialization for trained models (pickle is strictly forbidden)."""

from pathlib import Path
from typing import Any, Dict


def export_model_artifact(
    model: Any,
    metadata: Dict[str, Any],
    output_dir: Path,
) -> None:
    """Save model.json and metadata.json to destination directory."""
    raise NotImplementedError("ml_training.export.export_model_artifact is a stub")
