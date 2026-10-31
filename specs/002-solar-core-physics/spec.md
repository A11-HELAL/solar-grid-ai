# Feature Specification: Pure Physics Engine Module & Test Suite

**Feature Branch**: `002-solar-core-physics`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Build the pure physics engine module `solar_core/physics.py` and its comprehensive property/golden test suite `tests/test_physics.py`. Requirements: 1. Pure Functions Only: Must not import network, database, filesystem, or call `datetime.now()`. 2. Implement `calculate_solar_position(times: pd.DatetimeIndex, config: PlantConfig) -> pd.DataFrame` utilizing `pvlib.solarposition.get_solarposition` enforcing explicit UTC timestamps. 3. Implement `calculate_clear_sky_poa(times: pd.DatetimeIndex, config: PlantConfig) -> pd.Series` using `pvlib.clearsky.ineichen` and Transposition model `pvlib.irradiance.get_total_irradiance` matching site tilt (20 deg) and azimuth (0 deg North). 4. Implement `calculate_clear_sky_power(times: pd.DatetimeIndex, config: PlantConfig, cell_temp_c: Optional[pd.Series] = None) -> pd.Series` applying the system capacity (5.4 kWp), calibration factor (0.92), and temperature derating (gamma = -0.004/C, ref 25C). 5. Implement `is_night(clear_sky_power_kw: pd.Series, threshold_kw: float = 0.1) -> pd.Series` enforcing Engineering Decision #1. 6. Provide property tests verifying MR4 (night power identically 0) and golden test matching June/December Solstice known curves for Alice Springs. 7. Comply strictly with Hardware Rules: Sequential execution, no multiprocessing pools, pure type hints."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Solar Position & Transposed Irradiance (Priority: P1)

Solar-Grid AI core engineers and data transformation pipelines require pure mathematical functions to calculate exact solar position angles and transpose clear-sky irradiance to the fixed 20° tilt, 0° North azimuth plane for DKASC Site 14 using explicit UTC timestamps.

**Why this priority**: Solar angles and plane-of-array (POA) clear-sky irradiance form the absolute physical baseline for all downstream feature engineering, clear-sky ratio calculations, and model predictions.

**Independent Test**: Pass a DatetimeIndex of timestamps to `calculate_solar_position` and `calculate_clear_sky_poa` with `PlantConfig` (DKASC Site 14); verify exact column structures, monotonic rise/fall diurnal curves, and zero values when the sun is below the horizon.

**Acceptance Scenarios**:

1. **Given** a timezone-aware DatetimeIndex in UTC and a valid `PlantConfig`, **When** `calculate_solar_position` is called, **Then** return a DataFrame containing `apparent_zenith`, `zenith`, `apparent_elevation`, `elevation`, and `azimuth` without side effects.
2. **Given** a timezone-naive DatetimeIndex, **When** `calculate_solar_position` is called, **Then** raise a `ValueError` requiring explicit timezone awareness.
3. **Given** a DatetimeIndex spanning full 24-hour cycles, **When** `calculate_clear_sky_poa` is called, **Then** return a Series of plane-of-array irradiance ($W/m^2$) where all nighttime values (zenith > 90°) are strictly clamped to $0.0$.

---

### User Story 2 - Temperature-Derated Clear-Sky Power Modeling (Priority: P2)

ML feature engineers and soiling detection jobs need a calibrated baseline clear-sky power calculation incorporating array nameplate capacity (5.4 kWp), empirical calibration factor (0.92), inverter power limits (5.0 kW), and PV cell temperature derating ($\gamma = -0.004 / ^\circ\text{C}$).

**Why this priority**: Clear-sky power ($P_{clear\_sky}$) is the primary physical normalizer in feature extraction and the baseline for identifying soiling degradation and electrical faults.

**Independent Test**: Pass clear-sky timestamps and synthetic cell temperatures to `calculate_clear_sky_power`; verify that unheated panels produce nominal calibrated clear-sky power and that elevated cell temperatures ($T > 25^\circ\text{C}$) reduce output by exactly $0.4\%$ per $^\circ\text{C}$.

**Acceptance Scenarios**:

1. **Given** midday clear-sky irradiance and `cell_temp_c = None`, **When** `calculate_clear_sky_power` is called, **Then** return $P_{clear\_sky} = \frac{G_{poa}}{1000} \times \text{capacity\_kwp} \times \text{calibration\_factor}$, capped at inverter capacity.
2. **Given** identical irradiance and a series of `cell_temp_c = 45.0` ($+20^\circ\text{C}$ over reference $25^\circ\text{C}$), **When** `calculate_clear_sky_power` is called, **Then** output power is derated by exactly $\eta_{thermal} = 1 + (-0.004) \times (45 - 25) = 0.92$ ($8.0\%$ drop), satisfying thermal derating consistency.
3. **Given** nighttime timestamps, **When** `calculate_clear_sky_power` is called, **Then** power is identically $0.0$ kW regardless of cell temperature values.

---

### User Story 3 - Engineering Decision #1 Nighttime Clamping & Masking (Priority: P3)

Operational forecasting and data cleaning pipelines require strict daytime/nighttime segmentation to prevent sunrise/sunset ratio explosions and ensure zero nighttime power leaks.

**Why this priority**: Enforces Engineering Decision #1 audited from real Alice Springs telemetry: avoids near-zero division instability at twilight and clamps nighttime predictions to exactly 0.0 kW.

**Independent Test**: Pass a Series of clear-sky power values to `is_night(clear_sky_power_kw, threshold_kw=0.1)`; verify that every value $< 0.1$ kW evaluates to `True` and values $\ge 0.1$ kW evaluate to `False`.

**Acceptance Scenarios**:

1. **Given** a clear-sky power series containing values ranging from $0.0$ to $5.0$ kW, **When** `is_night(series, threshold_kw=0.1)` is executed, **Then** return a boolean Series where entries with $P < 0.1$ kW are `True` and $P \ge 0.1$ kW are `False`.
2. **Given** twilight boundary values ($0.099$ kW and $0.100$ kW), **When** evaluated, **Then** $0.099$ kW is classified as night (`True`) and $0.100$ kW is classified as day (`False`).

---

### User Story 4 - Metamorphic QA & Alice Springs Solstice Golden Tests (Priority: P4)

Quality assurance engineers and automated guards need a rigorous test suite in `tests/test_physics.py` validating MR4 (strict zero nighttime generation invariance) and golden solar curves for the June and December solstices in Alice Springs.

**Why this priority**: Guarantees that pure physics functions comply with the Metamorphic QA Catalog (MR4) and reproduce ground-truth solar geometry for DKASC Site 14 across extreme astronomical seasons.

**Independent Test**: Run `pytest tests/test_physics.py`; verify that metamorphic relation property tests pass with zero violations and solstice curves match known physical limits.

**Acceptance Scenarios**:

1. **Given** astronomical night conditions (zenith > 90° or `is_night == True`), **When** varying cell temperature or irradiance perturbations across test sweeps, **Then** output power remains identically $0.0$ kW (MR4 verification).
2. **Given** Alice Springs coordinates (Lat -23.7618, Lon 133.8748), **When** calculating clear-sky curves for June 21 (Winter Solstice), **Then** day length is approximately 10.3 hours, solar elevation peaks at $\approx 42.7^\circ$ (zenith $\approx 47.3^\circ$), and peak power is lower than summer.
3. **Given** Alice Springs coordinates, **When** calculating clear-sky curves for December 21 (Summer Solstice), **Then** day length is approximately 13.7 hours, solar elevation peaks near overhead ($\text{zenith} < 1^\circ$, elevation $\approx 89.6^\circ$), and peak power reaches summer clear-sky maximum.

---

### Edge Cases

- **Timezone-naive inputs**: Calling any physics function with a DatetimeIndex missing `tz` information MUST raise `ValueError` detailing that explicit UTC/timezone-aware timestamps are mandatory.
- **Sub-horizon sun angles**: When the sun is below the horizon (zenith > 90°), calculated DNI, GHI, POA, and clear-sky power MUST be non-negative and strictly clamped to $0.0$.
- **Extreme temperatures**: If `cell_temp_c` contains extreme values (e.g. $-40^\circ\text{C}$ or $+85^\circ\text{C}$), thermal derating must not produce negative power; power must remain bounded within $[0.0, \text{capacity\_kwp}]$.
- **Empty DatetimeIndex**: Passing an empty `pd.DatetimeIndex` MUST return an empty `pd.Series` or `pd.DataFrame` with matching dtypes and column names, without throwing exceptions.
- **Inverter capacity clipping**: Clear-sky AC power MUST NOT exceed `config.inverter_kw` (5.0 kW for Site 14).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `calculate_solar_position(times: pd.DatetimeIndex, config: PlantConfig) -> pd.DataFrame` as a pure function using `pvlib.solarposition.get_solarposition` without external I/O or system clock dependencies.
- **FR-002**: `calculate_solar_position` MUST validate that `times` is a timezone-aware DatetimeIndex; if timezone-naive, it MUST raise a descriptive `ValueError`.
- **FR-003**: System MUST implement `calculate_clear_sky_poa(times: pd.DatetimeIndex, config: PlantConfig) -> pd.Series` as a pure function utilizing `pvlib.clearsky.ineichen` and transposition model `pvlib.irradiance.get_total_irradiance`.
- **FR-004**: `calculate_clear_sky_poa` MUST transpose irradiance to the plant array tilt (`config.tilt_deg = 20.0`) and azimuth (`config.azimuth_deg = 0.0` North) and strictly clamp all nighttime and negative irradiance values to $0.0$ $W/m^2$.
- **FR-005**: System MUST implement `calculate_clear_sky_power(times: pd.DatetimeIndex, config: PlantConfig, cell_temp_c: Optional[pd.Series] = None) -> pd.Series` applying the plant capacity (`config.capacity_kwp = 5.4`), calibration factor (`config.calibration_factor = 0.92`), inverter ceiling (`config.inverter_kw = 5.0`), and cell temperature derating.
- **FR-006**: When `cell_temp_c` is provided to `calculate_clear_sky_power`, thermal derating MUST follow $\eta_{thermal} = 1.0 + \text{config.gamma\_per\_c} \times (T_{cell} - \text{config.ref\_temp\_c})$; when omitted, $\eta_{thermal} = 1.0$.
- **FR-007**: System MUST implement `is_night(clear_sky_power_kw: pd.Series, threshold_kw: float = 0.1) -> pd.Series` returning a boolean Series (`True` when power $< \text{threshold\_kw}$, `False` otherwise) enforcing Engineering Decision #1.
- **FR-008**: System MUST provide a comprehensive test suite in `tests/test_physics.py` covering unit validation, property tests for MR4 (night power identically 0), and golden solstice tests for Alice Springs.
- **FR-009**: The test suite in `tests/test_physics.py` MUST verify the June 21 (winter) and December 21 (summer) solstice diurnal curves for Alice Springs (Site 14: Lat -23.7618, Lon 133.8748), checking peak solar zenith, day length, and power bounds.
- **FR-010**: All modules and tests MUST adhere to host hardware rules: sequential execution only, no multiprocessing pools, pure type annotations, and zero network/filesystem/`datetime.now()` calls in physics functions.

### Key Entities

- **SolarPosition**: Tabular output of astronomical coordinates containing apparent zenith, true zenith, apparent elevation, true elevation, and azimuth angles.
- **ClearSkyPOA**: Series representing total plane-of-array irradiance ($W/m^2$) modeled under clear-sky atmospheric conditions transposed to array orientation.
- **ClearSkyPower**: Series representing theoretical electrical AC power output ($kW$) under clear-sky conditions, adjusted for empirical site calibration, temperature derating, and inverter clipping.
- **NightMask**: Boolean Series indicating whether the solar array is under nighttime/sub-threshold conditions ($P_{clear\_sky} < 0.1$ kW).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Execution time for calculating 1 full year of hourly solar positions and clear-sky power (8,760 timestamps) is under 250 milliseconds on dual-core Intel Core i5-7200U.
- **SC-002**: 100% of nighttime timestamps (zenith > 90° or `is_night == True`) yield exactly $0.0$ kW clear-sky power, achieving a 100% pass rate on MR4 property tests.
- **SC-003**: 100% pure functions: static inspection confirms zero imports of `datetime.now`, `requests`, `socket`, `sqlite3`, `psycopg2`, or filesystem write routines in `solar_core/physics.py`.
- **SC-004**: Alice Springs June Solstice test confirms day length within $10.3 \pm 0.5$ hours and peak solar elevation within $42.7^\circ \pm 1.0^\circ$.
- **SC-005**: Alice Springs December Solstice test confirms day length within $13.7 \pm 0.5$ hours and peak solar elevation within $89.6^\circ \pm 1.0^\circ$ (zenith $< 1.0^\circ$).
- **SC-006**: 100% test pass rate across `tests/test_physics.py` under single-threaded sequential pytest execution.

## Assumptions

- Timestamps provided to physics routines are timezone-aware `pd.DatetimeIndex` objects (or convert cleanly to UTC).
- Ineichen clear-sky model from `pvlib.clearsky.ineichen` is used with default Linke turbidity lookups supported by pvlib.
- Hay-Davies, Perez, or standard isotropic transposition models wrapped by `pvlib.irradiance.get_total_irradiance` are acceptable; standard `get_total_irradiance` defaults to the isotropic/transposition model.
- Temperature derating acts linearly based on $\gamma = -0.004 / ^\circ\text{C}$ relative to $25^\circ\text{C}$ STC.
- `PlantConfig` is imported from `solar_core.config`.
