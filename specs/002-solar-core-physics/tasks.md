# Tasks: Pure Physics Engine Module & Test Suite

**Input**: Design documents from `specs/002-solar-core-physics/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)

**Prerequisites**: `plan.md` (completed), `spec.md` (completed), `data-model.md` (completed), `contracts/` (completed)

**Organization**: Grouped into sequential phases and user story increments (US1, US2, US3, US4) to enable independent implementation, rigorous TDD verification, and strict sequential execution per Constitution Principle I.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Independent file / module task
- **[Story]**: Associated User Story (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Clear canonical file paths included in every task

---

## Phase 1: Setup Infrastructure

**Purpose**: Initialize module and test files for the pure physics engine in canonical package paths.

- [ ] T001 Initialize module skeleton `packages/solar_core/physics.py` with standard header, docstrings, type annotations, and pure standard library imports (`typing`, `pvlib`, `pandas`, `numpy`)
- [ ] T002 [P] Initialize test suite skeleton `tests/test_physics.py` with pytest fixtures for `PlantConfig` (DKASC Site 14) and synthetic timezone-aware DatetimeIndex ranges

---

## Phase 2: Foundational Physics Prerequisites

**Purpose**: Core validation utilities prerequisite for all physics functions.

- [ ] T003 Implement pure timezone validator helper in `packages/solar_core/physics.py` that verifies `pd.DatetimeIndex.tz is not None` and raises a descriptive `ValueError` for timezone-naive timestamps, normalizing timezone-aware indices to UTC

---

## Phase 3: User Story 1 - Deterministic Solar Position & Transposed Irradiance (Priority: P1) 🌟 MVP

**Goal**: Deliver pure functions `calculate_solar_position` and `calculate_clear_sky_poa` enforcing UTC timestamps, Ineichen clear-sky transposition for Site 14 (20° tilt, 0° North azimuth), and sub-horizon clamping.

**Independent Test**: Execute `pytest tests/test_physics.py -k "test_solar_position or test_clear_sky_poa"` to verify solar angle outputs, timezone-naive rejection, and clamped nighttime irradiance.

### Tests for User Story 1 (TDD First) 🧪

- [ ] T004 [P] [US1] Create unit tests in `tests/test_physics.py` covering:
  - `calculate_solar_position` with UTC DatetimeIndex returning DataFrame containing `apparent_zenith`, `zenith`, `apparent_elevation`, `elevation`, `azimuth`
  - `calculate_solar_position` raising `ValueError` when given timezone-naive DatetimeIndex
  - `calculate_clear_sky_poa` returning Series with name `"poa_clear_sky"` matching input index
  - Verification that `calculate_clear_sky_poa` clamps irradiance to exactly $0.0$ $W/m^2$ when `apparent_zenith >= 90.0`
  - Verification that clear-sky POA follows expected diurnal curve shape (peaks at solar noon, non-negative everywhere)

### Implementation for User Story 1

- [ ] T005 [US1] Implement `calculate_solar_position(times: pd.DatetimeIndex, config: PlantConfig) -> pd.DataFrame` in `packages/solar_core/physics.py` utilizing `pvlib.solarposition.get_solarposition` with site coordinates (`config.lat`, `config.lon`, `config.elevation_m`)
- [ ] T006 [US1] Implement `calculate_clear_sky_poa(times: pd.DatetimeIndex, config: PlantConfig) -> pd.Series` in `packages/solar_core/physics.py` using `pvlib.location.Location.get_clearsky(model='ineichen')` and `pvlib.irradiance.get_total_irradiance` (with `surface_tilt=config.tilt_deg`, `surface_azimuth=config.azimuth_deg`), clamping negative and sub-horizon values to $0.0$

**Checkpoint**: User Story 1 is completely functional and independently testable. Solar position and transposed clear-sky POA can be calculated deterministically.

---

## Phase 4: User Story 2 - Faiman Cell Temperature & Temperature-Derated Clear-Sky Power (Priority: P2)

**Goal**: Deliver empirical Faiman cell temperature calculation (`pvlib.temperature.faiman`) and calibrated clear-sky power incorporating array capacity ($5.4\text{ kWp}$), empirical calibration factor ($0.92$), inverter ceiling (`config.inverter_ac_cap_kw` = $5.0\text{ kW}$), and module temperature derating ($\gamma = -0.004 / ^\circ\text{C}$).

**Independent Test**: Execute `pytest tests/test_physics.py -k "test_faiman or test_clear_sky_power"` to verify Faiman cell temperatures, unheated power, thermal derating ratio, inverter ceiling clipping, and night zero power.

### Tests for User Story 2 (TDD First) 🧪

- [ ] T007 [P] [US2] Add unit tests in `tests/test_physics.py` for `calculate_faiman_cell_temperature`:
  - Validation against standard `pvlib.temperature.faiman` reference values ($u_0 = 25.0, u_1 = 6.84$)
  - Verification of wind speed defaulting: passing `wind_speed_ms=None` defaults to a deterministic `0.0 m/s` Series aligned to `poa_wm2.index`
  - Verification that `ValueError` is raised on NaN/Inf inputs, negative `poa_wm2`, negative `wind_speed_ms`, non-positive $u_0/u_1$, or index mismatch
- [ ] T008 [P] [US2] Add unit tests in `tests/test_physics.py` for `calculate_clear_sky_power`:
  - `calculate_clear_sky_power` with `cell_temp_c = None` applying base calibration ($P_{stc} \times 0.92$)
  - `calculate_clear_sky_power` with `cell_temp_c = 45.0` verifying exact thermal derating factor $\eta_{thermal} = 1 + (-0.004) \times (45 - 25) = 0.92$ ($8.0\%$ drop relative to $25^\circ\text{C}$)
  - Verification that clear-sky power is capped at `config.inverter_ac_cap_kw` ($5.0\text{ kW}$)
  - Verification that clear-sky power is strictly $0.0\text{ kW}$ at night regardless of `cell_temp_c` values

### Implementation for User Story 2

- [ ] T009 [US2] Implement `calculate_faiman_cell_temperature(poa_wm2: pd.Series, temp_air_c: pd.Series, wind_speed_ms: Optional[pd.Series] = None, u0: float = 25.0, u1: float = 6.84) -> pd.Series` in `packages/solar_core/physics.py`
- [ ] T010 [US2] Implement `calculate_clear_sky_power(times: pd.DatetimeIndex, config: PlantConfig, cell_temp_c: Optional[pd.Series] = None) -> pd.Series` in `packages/solar_core/physics.py` applying `config.capacity_kwp`, `config.calibration_factor`, linear thermal derating ($\gamma = \text{config.gamma\_per\_c}, T_{\text{ref}} = \text{config.ref\_temp\_c}$), and clipping to `config.inverter_ac_cap_kw` ($5.0\text{ kW}$)

**Checkpoint**: User Story 2 is functional. Cell temperatures and calibrated clear-sky power can be calculated deterministically.

---

## Phase 5: User Story 3 - Engineering Decision #1 Nighttime Clamping (`is_night`) (Priority: P3)

**Goal**: Implement robust day/night classification supporting both power threshold (`config.night_threshold_kw` = $0.1\text{ kW}$) and optional apparent solar zenith angle ($\ge 90.0^\circ$) to eliminate near-zero ratio instability.

**Independent Test**: Execute `pytest tests/test_physics.py -k "test_is_night"` to verify threshold classification, twilight boundary stability, and zenith override.

### Tests for User Story 3 (TDD First) 🧪

- [ ] T011 [P] [US3] Add unit tests in `tests/test_physics.py` covering:
  - `is_night` on synthetic Series: values $< 0.1\text{ kW}$ return `True`, values $\ge 0.1\text{ kW}$ return `False`
  - Boundary values: $0.0999\text{ kW}$ is `True`, $0.1000\text{ kW}$ is `False`
  - Custom threshold override support (e.g., `threshold_kw=0.05` or `config.night_threshold_kw`)
  - Verification that providing `apparent_zenith_deg >= 90.0` marks timestamps as night (`True`) even if power is non-zero

### Implementation for User Story 3

- [ ] T012 [US3] Implement `is_night(clear_sky_power_kw: pd.Series, threshold_kw: float = 0.1, apparent_zenith_deg: Optional[pd.Series] = None) -> pd.Series` in `packages/solar_core/physics.py` returning boolean Series mapping `(clear_sky_power_kw < threshold_kw) | (apparent_zenith_deg >= 90.0)` when zenith is provided, or `(clear_sky_power_kw < threshold_kw)` otherwise

**Checkpoint**: User Stories 1, 2, and 3 are complete, ensuring mathematical and numerical stability for day/night filtering.

---

## Phase 6: User Story 4 - Metamorphic QA & Alice Springs Solstice Golden Tests (Priority: P4)

**Goal**: Deliver property tests validating MR4 (strict zero nighttime generation invariance) and golden solar curves for June and December solstices in Alice Springs.

**Independent Test**: Execute `pytest tests/test_physics.py -k "test_mr4 or test_solstice"` to verify MR4 compliance and astronomical solstice bounds.

### Tests for User Story 4 🧪

- [ ] T013 [P] [US4] Implement MR4 property test `test_mr4_nighttime_zero_invariance` in `tests/test_physics.py` asserting that for all nighttime timestamps (zenith > 90° or `is_night == True`), varying cell temperature across $[-20^\circ\text{C}, 0^\circ\text{C}, 25^\circ\text{C}, 50^\circ\text{C}, 80^\circ\text{C}]$ produces identically $0.0\text{ kW}$ power with zero violations
- [ ] T014 [P] [US4] Implement golden test `test_alice_springs_june_solstice` in `tests/test_physics.py` verifying June 21 (winter) clear-sky curve: day length $10.3 \pm 0.5$ hours, solar noon zenith $47.3^\circ \pm 1.0^\circ$ (peak elevation $42.7^\circ \pm 1.0^\circ$), and peak power within $[3.2, 3.8]\text{ kW}$
- [ ] T015 [P] [US4] Implement golden test `test_alice_springs_december_solstice` in `tests/test_physics.py` verifying December 21 (summer) clear-sky curve: day length $13.7 \pm 0.5$ hours, solar noon zenith $< 1.0^\circ$ (peak elevation $89.6^\circ \pm 1.0^\circ$), and peak power reaching inverter saturation ceiling (`config.inverter_ac_cap_kw` = $5.0\text{ kW}$)

**Checkpoint**: Comprehensive QA and metamorphic validation suite is active, ensuring physical fidelity to Alice Springs astronomy.

---

## Phase 7: Polish, Aliases & Verification Quality Gate

**Purpose**: Backward compatibility aliases, package exports, static purity audit, and end-to-end test execution.

- [ ] T016 Implement backward compatibility aliases `compute_solar_position` and `compute_clear_sky_power` as thin wrappers in `packages/solar_core/physics.py`
- [ ] T017 Export physics functions (`calculate_solar_position`, `calculate_clear_sky_poa`, `calculate_faiman_cell_temperature`, `calculate_clear_sky_power`, `is_night`) in `packages/solar_core/__init__.py` and add to `__all__` list
- [ ] T018 Perform static inspection of `packages/solar_core/physics.py` verifying 100% pure functions: zero imports of `datetime.now`, `requests`, `socket`, `sqlite3`, `psycopg2`, or file write routines
- [ ] T019 Execute full test suite `pytest tests/test_physics.py -v --tb=short` verifying 100% test pass rate
- [ ] T020 Execute validation scenarios from `specs/002-solar-core-physics/quickstart.md`
- [ ] T021 Audit implementation against `solar-physics-guard` (MR4, Decision #1, DKASC Site 14 geometry, Faiman/thermal compatibility) and `clean-code-guard` (pure functional separation, strict sequential single-threaded execution)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Independent, executed first.
- **Foundational (Phase 2)**: Depends on Phase 1.
- **User Story 1 (Phase 3)**: Depends on Phase 2. Core MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 3 (`calculate_clear_sky_power` calls POA calculation and accepts Faiman cell temp).
- **User Story 3 (Phase 5)**: Depends on Phase 4 (`is_night` filters clear-sky power and checks solar zenith).
- **User Story 4 (Phase 6)**: Depends on Phases 3, 4, 5 (tests complete physics pipeline).
- **Polish & QA Gates (Phase 7)**: Runs after all user stories complete.

### Strict Sequential Execution Rule (Constitution Principle I)

Per Constitution Principle I, all tasks MUST execute in strict sequence:
`T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021`.
No parallel sub-agents or concurrent threads may be spawned.

---

## Implementation Strategy

### MVP Scope (Phase 1 through Phase 3)
Completing Phases 1–3 delivers deterministic solar positioning and transposed clear-sky POA irradiance for DKASC Site 14.

### Incremental Delivery
1. **Increment 1 (MVP)**: Solar position and transposed clear-sky POA (`T001`–`T006`).
2. **Increment 2**: Faiman cell temperature & calibrated/derated clear-sky power (`T007`–`T010`).
3. **Increment 3**: Engineering Decision #1 night masking with zenith support (`T011`–`T012`).
4. **Increment 4**: MR4 metamorphic test and Alice Springs solstice golden tests (`T013`–`T015`).
5. **Increment 5**: Aliases, package exports, static purity audit, full test execution (`T016`–`T021`).
