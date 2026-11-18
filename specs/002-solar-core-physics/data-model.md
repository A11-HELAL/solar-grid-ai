# Data Model & Physics Invariants: Pure Physics Engine Module

**Feature**: `002-solar-core-physics`  
**Date**: 2026-10-29 (Updated: 2026-11-18)  
**Location**: `packages/solar_core/physics.py`

## 1. Input & Output Data Structures

### Solar Position DataFrame (`pd.DataFrame`)
Returned by `calculate_solar_position(times: pd.DatetimeIndex, config: PlantConfig) -> pd.DataFrame`.

| Column | Type | Unit | Range | Description |
|---|---|---|---|---|
| `apparent_zenith` | `float64` | Degrees | $[0.0, 180.0]$ | Refraction-corrected solar zenith angle ($0^\circ = \text{overhead}$) |
| `zenith` | `float64` | Degrees | $[0.0, 180.0]$ | True geometric solar zenith angle |
| `apparent_elevation` | `float64` | Degrees | $[-90.0, 90.0]$ | Refraction-corrected solar elevation above horizon |
| `elevation` | `float64` | Degrees | $[-90.0, 90.0]$ | True geometric solar elevation |
| `azimuth` | `float64` | Degrees | $[0.0, 360.0]$ | Solar azimuth angle measured clockwise from North ($0^\circ = \text{North}$) |

Index: `pd.DatetimeIndex`, timezone-aware in UTC.

---

### Clear-Sky Plane-of-Array Irradiance (`pd.Series`)
Returned by `calculate_clear_sky_poa(times: pd.DatetimeIndex, config: PlantConfig) -> pd.Series`.

- **Type**: `pd.Series` (dtype: `float64`, name: `"poa_clear_sky"`)
- **Unit**: $W/m^2$
- **Physical Invariants**:
  - Nighttime clamping: $G_{poa} = 0.0$ when $\text{zenith} \ge 90.0^\circ$.
  - Non-negativity: $G_{poa} \ge 0.0$ for all timestamps.
  - Index: Identical to input `times` DatetimeIndex.

---

### Faiman Cell Temperature Series (`pd.Series`)
Returned by `calculate_faiman_cell_temperature(poa_wm2: pd.Series, temp_air_c: pd.Series, wind_speed_ms: Optional[pd.Series] = None, u0: float = 25.0, u1: float = 6.84) -> pd.Series`.

- **Type**: `pd.Series` (dtype: `float64`, name: `"temp_cell_c"`)
- **Unit**: $^\circ\text{C}$
- **Governing Equation (Faiman Model)**:
  $$T_{\text{cell}} = T_{\text{air}} + \frac{G_{\text{poa}}}{u_0 + u_1 \times v_{\text{wind}}}$$
  Implemented via `pvlib.temperature.faiman(poa_global=poa_wm2, temp_air=temp_air_c, wind_speed=wind_speed_ms, u0=u0, u1=u1)`.
- **Wind Speed Defaulting**:
  If `wind_speed_ms is None`, defaults deterministically to `0.0 m/s` (Series of zeros matching `poa_wm2.index`).
- **Physical Invariants & Validation**:
  - Irradiance non-negativity: $G_{\text{poa}} \ge 0.0$ ($W/m^2$).
  - Wind speed non-negativity: $v_{\text{wind}} \ge 0.0$ ($m/s$).
  - Heat loss coefficients: $u_0 > 0.0$ and $u_1 > 0.0$ (standard open-rack defaults: $u_0 = 25.0$, $u_1 = 6.84$).
  - Strict Finite Data: Raises `ValueError` on any `NaN` or `Inf` in inputs.
  - Index Consistency: Raises `ValueError` if indices of `poa_wm2`, `temp_air_c`, or `wind_speed_ms` do not match.

---

### Calibrated Clear-Sky Power Output (`pd.Series`)
Returned by `calculate_clear_sky_power(times: pd.DatetimeIndex, config: PlantConfig, cell_temp_c: Optional[pd.Series] = None) -> pd.Series`.

- **Type**: `pd.Series` (dtype: `float64`, name: `"clear_sky_power_kw"`)
- **Unit**: $kW$
- **Governing Equations**:
  $$P_{stc} = \frac{G_{poa}}{1000.0} \times \text{config.capacity\_kwp}$$
  $$\eta_{thermal} = 1.0 + \text{config.gamma\_per\_c} \times (T_{cell} - \text{config.ref\_temp\_c}) \quad (\text{if } T_{cell} \text{ given, else } 1.0)$$
  $$P_{dc} = P_{stc} \times \text{config.calibration\_factor} \times \eta_{thermal}$$
  $$P_{clear\_sky} = \min(P_{dc}, \text{config.inverter\_ac\_cap\_kw})$$
- **Physical Invariants**:
  - Bounded within $[0.0, \text{config.inverter\_ac\_cap\_kw}]$ ($5.0\text{ kW}$).
  - Zero night power: When $G_{poa} == 0.0$, $\text{zenith} \ge 90.0^\circ$, or $P_{clear\_sky} < \text{config.night\_threshold\_kw}$ ($0.1\text{ kW}$), power is clamped strictly to $0.0\text{ kW}$.
  - Thermal monotonicity (MR2/MR3): $\frac{\partial P}{\partial T_{cell}} \le 0$ during daytime.

---

### Nighttime Mask Series (`pd.Series`)
Returned by `is_night(clear_sky_power_kw: pd.Series, threshold_kw: float = 0.1, apparent_zenith_deg: Optional[pd.Series] = None) -> pd.Series`.

- **Type**: `pd.Series` (dtype: `bool`, name: `"is_night"`)
- **Default Threshold**: `threshold_kw = config.night_threshold_kw = 0.1` kW (Engineering Decision #1).
- **Mapping**:
  $$\text{is\_night} = \begin{cases} (P_{clear\_sky} < \text{threshold\_kw}) \lor (\text{apparent\_zenith\_deg} \ge 90.0^\circ) & \text{if apparent\_zenith\_deg provided} \\ (P_{clear\_sky} < \text{threshold\_kw}) & \text{otherwise} \end{cases}$$
- **Physical Meaning**: Identifies periods where astronomical horizon cutoff or inverter minimum generation thresholds prevent grid export.
