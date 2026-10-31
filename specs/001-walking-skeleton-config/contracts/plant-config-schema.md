# Contract: `plant_config.yaml` Schema

## Format & Location
- **Location**: `plant_config.yaml` (repository root)
- **Format**: YAML 1.2 (UTF-8 encoded)
- **Authority**: Locked constants for DKA Solar Centre Site 14 (`dka_01`)

## Full YAML Representation
```yaml
# ==============================================================================
# Solar-Grid AI v1.1 - Authoritative Plant Configuration (DKASC Site 14)
# ==============================================================================
plant:
  id: "dka_01"
  name: "DKA Solar Centre Site 14"
  location:
    lat: -23.7618
    lon: 133.8748
    elevation_m: 545.0
    tz: "Australia/Darwin"

array:
  capacity_kwp: 5.4
  inverter_ac_cap_kw: 5.0
  tilt_deg: 20.0
  azimuth_deg: 0.0

physics:
  gamma_per_c: -0.004
  ref_temp_c: 25.0
  calibration_factor: 0.92
  night_threshold_kw: 0.1
```

## Schema Validation Constraints

```yaml
type: object
required:
  - plant
  - array
  - physics
properties:
  plant:
    type: object
    required: [id, location]
    properties:
      id:
        type: string
        minLength: 1
      name:
        type: string
      location:
        type: object
        required: [lat, lon, elevation_m, tz]
        properties:
          lat:
            type: number
            minimum: -90.0
            maximum: 90.0
          lon:
            type: number
            minimum: -180.0
            maximum: 180.0
          elevation_m:
            type: number
            minimum: -500.0
          tz:
            type: string
  array:
    type: object
    required: [capacity_kwp, inverter_ac_cap_kw, tilt_deg, azimuth_deg]
    properties:
      capacity_kwp:
        type: number
        exclusiveMinimum: 0.0
      inverter_ac_cap_kw:
        type: number
        exclusiveMinimum: 0.0
      tilt_deg:
        type: number
        minimum: 0.0
        maximum: 90.0
      azimuth_deg:
        type: number
        minimum: 0.0
        maximum: 360.0
  physics:
    type: object
    required: [gamma_per_c, ref_temp_c, calibration_factor, night_threshold_kw]
    properties:
      gamma_per_c:
        type: number
        exclusiveMaximum: 0.0
      ref_temp_c:
        type: number
        exclusiveMinimum: 0.0
      calibration_factor:
        type: number
        exclusiveMinimum: 0.0
        maximum: 1.5
      night_threshold_kw:
        type: number
        exclusiveMinimum: 0.0
```
