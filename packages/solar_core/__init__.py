"""Solar-Grid AI pure physics and domain engine (Room 2)."""

from .config import PlantConfig, load_plant_config

CORE_VERSION = "1.1.0"
__version__ = CORE_VERSION

__all__ = ["CORE_VERSION", "__version__", "PlantConfig", "load_plant_config"]
