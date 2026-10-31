# Contract: `packages/solar_core/config.py` Module Interface

## Module Signature & Pure Function Contract

### Public Exports
```python
from pathlib import Path
from typing import Union
from dataclasses import dataclass

__all__ = ["PlantConfig", "load_plant_config"]
```

### Function Signature: `load_plant_config`
```python
def load_plant_config(path: Union[str, Path]) -> PlantConfig:
    """Load, parse, and validate plant configuration from a YAML file.

    Parameters:
        path: Path to the plant_config.yaml file.

    Returns:
        PlantConfig: Validated, immutable plant configuration instance.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        ValueError: If YAML syntax is invalid, required fields are missing,
                    or physical values violate invariant bounds.
    """
```

### Purity Guarantees
- **No System Clock**: Does not call `datetime.now()`, `datetime.utcnow()`, or `time.time()`.
- **No Database**: Does not import database drivers (`psycopg2`, `asyncpg`, `sqlalchemy`).
- **No Network**: Does not make HTTP or socket requests.
- **No Pickle**: Does not use Python `pickle`.
- **Side Effect Free**: Deterministic output strictly determined by input file content.
