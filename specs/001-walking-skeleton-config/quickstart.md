# Quickstart & Validation Guide: 001-walking-skeleton-config

## 1. Prerequisites
- Python 3.11+
- Virtual environment activated with required baseline dependencies:
  ```bash
  pip install -r requirements.txt
  pip install -e packages/solar_core
  ```

## 2. Verification Scenarios

### Scenario A: Monorepo 8-Room Layout Verification
Run a verification command to ensure all 8 rooms exist with proper stubs and no generic `src/` exists:
```bash
python -c "
from pathlib import Path
rooms = ['data_pipeline', 'packages/solar_core', 'ml_training', 'db', 'worker', 'api', 'ui', 'tests']
assert not Path('src').exists(), 'Violation: Generic src/ directory found!'
for r in rooms:
    assert Path(r).is_dir(), f'Missing room: {r}'
print('All 8 rooms successfully verified!')
"
```
**Expected Output**:
```text
All 8 rooms successfully verified!
```

### Scenario B: Unit Test Suite Execution
Execute the Room 2 configuration unit tests:
```bash
pytest tests/test_config.py -v
```
**Expected Output**:
```text
tests/test_config.py::test_load_plant_config_valid PASSED
tests/test_config.py::test_plant_config_immutability PASSED
tests/test_config.py::test_load_plant_config_missing_file PASSED
tests/test_config.py::test_load_plant_config_positive_gamma PASSED
tests/test_config.py::test_load_plant_config_negative_tilt PASSED
tests/test_config.py::test_load_plant_config_tilt_over_90 PASSED
tests/test_config.py::test_load_plant_config_inverter_exceeds_capacity PASSED
tests/test_config.py::test_load_plant_config_invalid_calibration_factor PASSED
tests/test_config.py::test_load_plant_config_malformed_yaml PASSED
tests/test_config.py::test_load_plant_config_missing_fields PASSED
============================== 10 passed in 0.05s ==============================
```

### Scenario C: OpenAPI Contract Validation
Verify the OpenAPI specification:
```bash
python -c "
import json
from pathlib import Path
spec = json.loads(Path('docs/openapi.json').read_text(encoding='utf-8'))
assert spec['openapi'].startswith('3.'), 'Invalid OpenAPI version'
assert len(spec['paths']) == 8, f'Expected 8 endpoints, found {len(spec[\"paths\"])}'
print('OpenAPI contract validated: 8 endpoints present.')
"
```
**Expected Output**:
```text
OpenAPI contract validated: 8 endpoints present.
```
