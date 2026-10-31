# Data Model: Foundational Solar Core Configuration & Contracts

**Feature**: `001-solar-core-config`
**Date**: 2026-10-26

## 1. Core Entities (Immutable Dataclasses)

### PlantConfig
Represents the physical, geographical, and operational design constants of the solar photovoltaic generation plant.

```python
@dataclass(frozen=True, slots=True)
class PlantConfig:
    plant_id: str = "dka_01"
    lat: float = -23.7618
    lon: float = 133.8748
    elevation_m: float = 545.0
    tz: str = "Australia/Darwin"
    capacity_kwp: float = 5.4
    inverter_kw: float = 5.0
    tilt_deg: float = 20.0
    azimuth_deg: float = 0.0
    gamma_per_c: float = -0.004
    ref_temp_c: float = 25.0
    calibration_factor: float = 0.92
    night_clear_sky_threshold_kw: float = 0.1
    max_short_gap_hours: int = 2
```

#### Fields & Validation Invariants

| Field | Type | Default | Valid Range / Format | Physical Meaning |
|---|---|---|---|---|
| `plant_id` | `str` | `"dka_01"` | Non-empty alphanumeric/underscore | Plant identifier (DKASC Site 14) |
| `lat` | `float` | `-23.7618` | $[-90.0, 90.0]$ | Latitude in decimal degrees (Alice Springs) |
| `lon` | `float` | `133.8748` | $[-180.0, 180.0]$ | Longitude in decimal degrees |
| `elevation_m` | `float` | `545.0` | $[-500.0, 9000.0]$ | Elevation above sea level in meters |
| `tz` | `str` | `"Australia/Darwin"` | Valid IANA timezone | Timezone (UTC+09:30 fractional offset) |
| `capacity_kwp` | `float` | `5.4` | $> 0.0$ | Total DC nameplate capacity in kWp |
| `inverter_kw` | `float` | `5.0` | $0.0 < \text{inverter\_kw} \le \text{capacity\_kwp}$ | Inverter continuous AC capacity in kW |
| `tilt_deg` | `float` | `20.0` | $[0.0, 90.0]$ | Fixed array tilt angle above horizontal |
| `azimuth_deg` | `float` | `0.0` | $[0.0, 360.0]$ | Array azimuth ($0.0^\circ = \text{North}$ in Southern Hemisphere) |
| `gamma_per_c` | `float` | `-0.004` | $[-0.015, -0.0001]$ | PV temperature power coefficient ($\% / ^\circ\text{C} / 100$) |
| `ref_temp_c` | `float` | `25.0` | $[0.0, 50.0]$ | Standard test conditions reference temperature |
| `calibration_factor` | `float` | `0.92` | $[0.5, 1.5]$ | Clear-sky empirical calibration factor |
| `night_clear_sky_threshold_kw` | `float` | `0.1` | $> 0.0$ | Threshold below which `is_night = True` |
| `max_short_gap_hours` | `int` | `2` | $\ge 1$ | Maximum continuous gap permitted for linear interpolation |

---

### SoilingConfig
Encapsulates operational parameters, clipping filters, rolling evaluation window sizes, and progressive cleaning alarm limits.

```python
@dataclass(frozen=True, slots=True)
class SoilingConfig:
    min_poa_wm2: float = 500.0
    max_unclipped_power_kw: float = 4.95
    min_valid_hours: int = 4
    rolling_window_days: int = 7
    baseline_clean_days: int = 14
    watch_loss_pct: float = 2.0
    clean_alert_loss_pct: float = 4.0
    recovery_jump_pct: float = 2.0
    fault_drop_pct: float = 10.0
```

#### Fields & Validation Invariants

| Field | Type | Default | Valid Range | Operational Meaning |
|---|---|---|---|---|
| `min_poa_wm2` | `float` | `500.0` | $\ge 200.0$ | Irradiance threshold for stable daytime performance ratio |
| `max_unclipped_power_kw` | `float` | `4.95` | $> 0.0$ | Clipping ceiling (inverter clips at 5.0 kW; 4.95 kW avoids distortion) |
| `min_valid_hours` | `int` | `4` | $\ge 1$ | Minimum qualifying unclipped hours required per day |
| `rolling_window_days` | `int` | `7` | $\ge 3$ | Rolling median aggregation window for PR trend line |
| `baseline_clean_days` | `int` | `14` | $\ge 5$ | Window used to establish post-cleaning clean baseline PR |
| `watch_loss_pct` | `float` | `2.0` | $> 0.0$ | Early warning threshold for observed soiling derating |
| `clean_alert_loss_pct` | `float` | `4.0` | $> \text{watch\_loss\_pct}$ | Actionable cleaning recommendation threshold |
| `recovery_jump_pct` | `float` | `2.0` | $> 0.0$ | Minimum positive PR jump indicating a rainfall or wash event |
| `fault_drop_pct` | `float` | `10.0` | $> \text{clean\_alert\_loss\_pct}$ | Instant drop indicating inverter or module string failure |

---

### ValidatorConfig
Encapsulates data cleaning tolerances, physical headroom limits, and operational intervention alert rates.

```python
@dataclass(frozen=True, slots=True)
class ValidatorConfig:
    clear_sky_headroom_factor: float = 1.1
    warn_intervention_rate_pct: float = 5.0
    critical_intervention_rate_pct: float = 15.0
```

#### Fields & Validation Invariants

| Field | Type | Default | Valid Range | Operational Meaning |
|---|---|---|---|---|
| `clear_sky_headroom_factor` | `float` | `1.1` | $[1.0, 1.5]$ | Allowable physical power headroom above theoretical clear-sky |
| `warn_intervention_rate_pct` | `float` | `5.0` | $[0.0, 50.0]$ | Telemetry interpolation/imputation rate triggering a warning |
| `critical_intervention_rate_pct` | `float` | `15.0` | $> \text{warn\_intervention\_rate\_pct}$ | Telemetry corruption rate triggering day-level invalidation |

---

## 2. Canonical Contracts & Constants

```python
QUALITY_FLAGS: tuple[str, ...] = (
    "ok",
    "interpolated",
    "missing",
    "fault_suspect",
    "out_of_range",
)

RAW_DKA_SHA256: str = "eaa2a6515f77bb226315816639528d75e68a6ba9a4f6fdded1943d99736523e0"

FEATURE_COLUMNS: tuple[str, ...] = (
    "poa_wm2",
    "temp_air_c",
    "wind_ms",
    "temp_module_c",
    "clear_sky_kw",
    "cloud_cover",
    "zenith_deg",
    "azimuth_deg",
    "hour",
    "day_of_year",
    "power_kw_lag_1h",
    "power_kw_lag_24h",
)
```
