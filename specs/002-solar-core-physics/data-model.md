# Data Model & Physics Invariants: Pure Physics Engine Module

**Feature**: `002-solar-core-physics`
**Date**: 2026-10-29

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

### Calibrated Clear-Sky Power Output (`pd.Series`)
Returned by `calculate_clear_sky_power(times: pd.DatetimeIndex, config: PlantConfig, cell_temp_c: Optional[pd.Series] = None) -> pd.Series`.

- **Type**: `pd.Series` (dtype: `float64`, name: `"clear_sky_power_kw"`)
- **Unit**: $kW$
- **Governing Equations**:
  $$P_{stc} = \frac{G_{poa}}{1000.0} \times \text{config.capacity\_kwp}$$
  $$\eta_{thermal} = 1.0 + \text{config.gamma\_per\_c} \times (T_{cell} - \text{config.ref\_temp\_c}) \quad (\text{if } T_{cell} \text{ given, else } 1.0)$$
  $$P_{dc} = P_{stc} \times \text{config.calibration\_factor} \times \eta_{thermal}$$
  $$P_{clear\_sky} = \min(P_{dc}, \text{config.inverter\_kw})$$
- **Physical Invariants**:
  - Bounded within $[0.0, \text{config.inverter\_kw}]$.
  - Zero night power: When $G_{poa} == 0.0$ or $\text{zenith} \ge 90.0^\circ$, $P_{clear\_sky} \equiv 0.0$ kW.
  - Thermal monotonicity (MR2/MR3): $\frac{\partial P}{\partial T_{cell}} \le 0$ during daytime.

---

### Nighttime Mask Series (`pd.Series`)
Returned by `is_night(clear_sky_power_kw: pd.Series, threshold_kw: float = 0.1) -> pd.Series`.

- **Type**: `pd.Series` (dtype: `bool`, name: `"is_night"`)
- **Mapping**:
  $$\text{is\_night} = (P_{clear\_sky} < \text{threshold\_kw})$$
- **Physical Meaning**: Identifies periods where astronomical or inverter cutoff prevents meaningful generation.
