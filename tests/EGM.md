# Room 8: Testing Suite & Metamorphic Gate (`tests/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`tests` houses the automated test harness, physical property tests, contract validation, layout assertions, and the Metamorphic QA Gate (MR1-MR8) for Solar-Grid AI.

### Locked Architectural Invariants
- **No Generic `src/` Directory**: Validated by `test_layout.py`. Any attempt to introduce `src/` fails CI immediately.
- **Authoritative Contract Gate**: `test_contract.py` enforces OpenAPI 3.0 specification compliance across all 8 analytical endpoints.
- **Strict Physical Parameter Boundary Testing**: `test_config.py` validates that non-physical plant configurations (e.g., negative capacity, positive thermal coefficient, tilt outside [0, 90]) are rejected with `ValueError`.
- **Zero-NaN Weather Ingestion**: `test_weather_ingest.py` ensures missing values in raw weather feeds fail fast.
- **Metamorphic QA Gate (MR1-MR8)**: All production models must pass the 8 metamorphic sanity relations with $\ge 95\%$ compliance before deployment.

---

## 2. Metamorphic Relations Catalog (MR1 - MR8)

| Relation | Domain Property | Mathematical / Physical Invariant |
| :--- | :--- | :--- |
| **MR1** | Irradiance Monotonicity | $+100\text{ W/m}^2$ daytime POA irradiance held constant elsewhere $\implies \frac{\partial P}{\partial G} \ge 0$. |
| **MR2** | Thermal Monotonicity | $T_{\text{ambient}}$ increases from $25^\circ\text{C}$ to $45^\circ\text{C}$ $\implies P_{\text{hot}} / P_{\text{base}} \in [0.85, 0.97]$ (theoretical $\approx 0.92$). |
| **MR3** | Cloud Opacity Damping | Increasing cloud cover percentage held constant elsewhere $\implies \frac{\partial P}{\partial C} \le 0$. |
| **MR4** | Nighttime Invariance | Solar zenith $> 90^\circ$ or clear sky $< 0.1\text{ kW} \implies P_{\text{pred}} \equiv 0.0\text{ kW}$ regardless of weather perturbations. |
| **MR5** | Timezone Invariance | Telemetry evaluated under `Australia/Darwin` local time vs UTC representation $\implies$ identical predictions. |
| **MR6** | Capacity Scaling | Doubling array capacity in config ($5.4 \to 10.8\text{ kWp}$) $\implies$ doubles predicted output before inverter clipping. |
| **MR7** | Soiling Continuity | Multiplying power measurements by $0.9$ uniformly $\implies$ identical estimated degradation rate (%/day). |
| **MR8** | Dust Accumulation Monotonicity | Increasing synthetic dust accumulation rate $\implies$ triggers cleaning alerts on or before the baseline date. |

---

## 3. Current Implementation Status (25 Passing Tests)

The test suite currently runs **25 passing tests** under `pytest`:
- **`test_config.py` (15 passing tests)**:
  - Validates immutable defaults of `PlantConfig`.
  - Validates `load_plant_config("plant_config.yaml")` matches DKASC Site 14 parameters.
  - Asserts immutability (`dataclasses.FrozenInstanceError` upon mutation).
  - Validates rejection of non-existent files (`FileNotFoundError`), malformed YAML, inverted capacity/inverter ratios, out-of-range tilts, positive $\gamma$, and invalid calibration factors.
- **`test_weather_ingest.py` (6 passing tests)**:
  - Validates schema and column order of `data/raw/open_meteo_dka_2023_2025.csv`.
  - Validates UTC timestamp parsing, chronological sorting, and zero-NaN integrity.
  - Tests rejection of corrupted or missing CSV paths.
- **`test_layout.py` (3 passing tests)**:
  - Asserts absence of generic `src/` directory.
  - Validates presence of all 8 decoupled rooms.
  - Validates operational staging folders (`data/raw`, `data/processed`, `models/ACTIVE`).
- **`test_contract.py` (1 passing test)**:
  - Validates `docs/openapi.json` OpenAPI 3.0 validity and coverage of all 8 endpoints.
- **Sprint 2 Roadmap**: Metamorphic gate runner (`test_metamorphic.py`) and solstice golden tests (`test_physics.py`).
