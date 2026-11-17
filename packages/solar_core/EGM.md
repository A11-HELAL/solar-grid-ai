# Room 2: Pure Solar Core (`packages/solar_core/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`solar_core` is the mathematical domain engine of Solar-Grid AI. It encapsulates all solar geometries, physical clear-sky models, thermal deratings, feature transformations, physical guardrails, and soiling estimation logic.

### Pure Functional Invariants (Constitution Principle II)
- **100% Pure Deterministic Math**: Strictly zero database drivers, zero network/HTTP requests, zero web framework imports (`fastapi`, etc.).
- **Zero System Clock Queries**: `datetime.now()`, `datetime.utcnow()`, and `time.time()` are strictly forbidden. All timestamps and time indices must be passed explicitly as `pd.DatetimeIndex` or `datetime` arguments.
- **Zero Pickle Serialization**: No `.pkl` dumping or loading.
- **Linear Internal Dependency Chain**:
  $$\text{config.py} \longrightarrow \text{physics.py} \longrightarrow \begin{cases} \text{features.py} \\ \text{validator.py} \end{cases} \longrightarrow \text{soiling.py} \longrightarrow \text{sim.py}$$

---

## 2. Module Roster & Architectural Contracts

### `config.py` (Current Status: IMPLEMENTED - 15 Passing Tests)
- **`PlantConfig`**: Frozen immutable dataclass (`frozen=True`, `slots=True`) locking DKASC Site 14 (`dka_01`) constants:
  - `plant_id`: `"dka_01"`
  - `lat`: `-23.7618`, `lon`: `133.8748`, `elevation_m`: `545.0`, `tz`: `"Australia/Darwin"`
  - `capacity_kwp`: `5.4` kWp DC, `inverter_ac_cap_kw`: `5.0` kW AC
  - `tilt_deg`: `20.0°`, `azimuth_deg`: `0.0°` (True North)
  - `gamma_per_c`: `-0.004 / °C`, `ref_temp_c`: `25.0 °C`
  - `calibration_factor`: `0.92`, `night_threshold_kw`: `0.1 kW`
- **`load_plant_config(path)`**: Pure parser validating physical bounds:
  - `capacity_kwp > inverter_ac_cap_kw > 0.0`
  - `0.0 <= tilt_deg <= 90.0`, `0.0 <= azimuth_deg < 360.0`
  - `gamma_per_c < 0.0`, `0.0 < calibration_factor <= 1.5`, `night_threshold_kw > 0.0`
  - Raises `FileNotFoundError` or descriptive `ValueError`.

### `physics.py` (Current Status: SKELETON CONTRACT - Sprint 1)
- **`compute_solar_position(timestamps_utc, lat, lon, elevation_m)`**: Deterministic solar zenith, apparent zenith, azimuth via `pvlib`. Requires timezone-aware UTC timestamps.
- **`compute_clear_sky_power(solar_position, capacity_kwp, tilt_deg, azimuth_deg, gamma_per_c, calibration_factor)`**: Transposed plane-of-array irradiance ($G_{\text{poa}}$ via Ineichen/Perez), scaled to nameplate capacity (5.4 kWp), adjusted by empirical calibration factor (0.92), and derated for cell temperature:
  $$P_{\text{clear\_sky}} = \min\left(5.0, \frac{G_{\text{poa}}}{1000} \times 5.4 \times 0.92 \times [1 + \gamma (T_{\text{cell}} - 25)]\right)$$
- **Faiman Module Temperature**: Imputed cell temperature via `pvlib.temperature.faiman(poa_wm2, temp_air_c, wind_ms)`.
- **`is_night(clear_sky_kw, threshold_kw=0.1)`**: Enforces Engineering Decision #1. Evaluates to `True` whenever $P_{\text{clear\_sky}} < 0.1$ kW or solar zenith $> 90^\circ$. Clamps nighttime power strictly to $0.0$.

### `features.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`extract_features(telemetry_df)`**: Generates 16 canonical `FEATURE_COLUMNS`:
  - Temporal: `hour_sin`, `hour_cos`, `day_of_year_sin`, `day_of_year_cos`
  - Solar Geometry: `solar_zenith`, `solar_azimuth`, `clear_sky_kw`
  - Weather: `poa_wm2`, `temp_air_c`, `wind_speed_ms`, `cloud_cover_pct`
  - Lags & Dynamics: `power_lag_1h`, `power_lag_2h`, `power_lag_24h`, `poa_rolling_3h_mean`
  - Target Ratio: $r = \text{clip}(P_{\text{actual}} / P_{\text{clear\_sky}}, 0.0, 1.1)$

### `validator.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`apply_guardrails(...) -> GuardrailResult`**: Hard physical filters protecting grid consumers:
  - **H1 (Finite Check)**: NaN/Inf $\to$ trigger fallback (`rule_hit = 'H1_NAN_OR_INF'`).
  - **H2 (Night Zeroing)**: If `is_night == True` and prediction $> 0.0 \to$ clamp to $0.0$ (`rule_hit = 'H2_NIGHT_ZERO'`).
  - **H3 (Non-Negativity)**: If prediction $< 0.0 \to$ clamp to $0.0$ (`rule_hit = 'H3_NEGATIVE_CLIP'`).
  - **H4 (Clear-Sky Ceiling)**: If prediction $> 1.1 \times P_{\text{clear\_sky}} \to$ clamp to $1.1 \times P_{\text{clear\_sky}}$ (`rule_hit = 'H4_CLEAR_SKY_CAP'`).
  - **H5 (Capacity Ceiling)**: If prediction $> 5.0\text{ kW} \to$ clamp to $5.0\text{ kW}$ (`rule_hit = 'H5_CAPACITY_CAP'`).
  - **Soft Suspicion Alert S1**: Daytime $P_{\text{clear\_sky}} \ge 2.0\text{ kW}$, cloud cover $< 20\%$, and $P_{\text{pred}} < 0.15 \times P_{\text{clear\_sky}} \to$ flag `'S1_LOW_CLEAR_DAY_WARN'`.

### `soiling.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`compute_daily_pr_tc(hourly_df, inverter_ceiling_kw=4.95, min_poa_wm2=500.0)`**:
  - Filters unclipped, stable high-irradiance hours ($G_{\text{poa}} \ge 500\text{ W/m}^2$ and $P < 4.95\text{ kW}$, requiring $\ge 4$ valid hours/day).
  - Computes temperature-corrected Performance Ratio ($\text{PR}_{\text{tc}}$) and 14-day rolling median ($\text{PR}_{\text{smooth}}$).
  - Calculates daily soiling loss percentage and classifies status (`clean`, `soiled`, `critical_wash_needed`, `fault_suspect`).

### `sim.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`generate_synthetic_profile(timestamps_utc, capacity_kwp)`**: Generates deterministic synthetic telemetry for testing, including soiling ramps, inverter tripping faults, and sensor drifts.
