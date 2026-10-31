# File Contract: `plant_config.yaml` Schema

**Feature**: `001-solar-core-config`
**Date**: 2026-10-26

## 1. Schema Definition

Root file `plant_config.yaml` MUST follow this structure with exact field naming and verified parameters for DKASC Site 14 (`dka_01`):

```yaml
# Solar-Grid AI v1.1 - DKASC Site 14 Plant Configuration
plant_id: "dka_01"
lat: -23.7618
lon: 133.8748
elevation_m: 545.0
tz: "Australia/Darwin"
capacity_kwp: 5.4
inverter_kw: 5.0
tilt_deg: 20.0
azimuth_deg: 0.0
gamma_per_c: -0.004
ref_temp_c: 25.0
calibration_factor: 0.92
night_clear_sky_threshold_kw: 0.1
max_short_gap_hours: 2
```

## 2. Constraints & Data Types

| Key | Type | Required | Default | Constraint |
|---|---|---|---|---|
| `plant_id` | `str` | Yes | `"dka_01"` | Non-empty string |
| `lat` | `float` | Yes | `-23.7618` | $-90.0 \le \text{lat} \le 90.0$ |
| `lon` | `float` | Yes | `133.8748` | $-180.0 \le \text{lon} \le 180.0$ |
| `elevation_m` | `float` | Yes | `545.0` | $-500.0 \le \text{elevation\_m} \le 9000.0$ |
| `tz` | `str` | Yes | `"Australia/Darwin"` | Recognized IANA Timezone string |
| `capacity_kwp` | `float` | Yes | `5.4` | $\text{capacity\_kwp} > 0.0$ |
| `inverter_kw` | `float` | Yes | `5.0` | $0.0 < \text{inverter\_kw} \le \text{capacity\_kwp}$ |
| `tilt_deg` | `float` | Yes | `20.0` | $0.0 \le \text{tilt\_deg} \le 90.0$ |
| `azimuth_deg` | `float` | Yes | `0.0` | $0.0 \le \text{azimuth\_deg} \le 360.0$ |
| `gamma_per_c` | `float` | Yes | `-0.004` | $-0.015 \le \text{gamma\_per\_c} \le -0.0001$ |
| `ref_temp_c` | `float` | Yes | `25.0` | $0.0 \le \text{ref\_temp\_c} \le 50.0$ |
| `calibration_factor` | `float` | Yes | `0.92` | $0.5 \le \text{calibration\_factor} \le 1.5$ |
| `night_clear_sky_threshold_kw` | `float` | Yes | `0.1` | $\text{night\_clear\_sky\_threshold\_kw} > 0.0$ |
| `max_short_gap_hours` | `int` | Yes | `2` | $\text{max\_short\_gap\_hours} \ge 1$ |
