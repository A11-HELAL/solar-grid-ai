# Room 4: Relational Database (`db/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`db` defines the authoritative relational schema, initialization scripts, seed fixtures, and migration definitions for Solar-Grid AI's PostgreSQL 16 database.

### Locked Architectural Invariants
- **Database Engine**: PostgreSQL 16+.
- **UTC Timezone Standard**: All temporal coordinates and horizons MUST use `TIMESTAMPTZ` (stored and indexed in UTC).
- **Quality Flag Enforcement**: The `measurements.quality_flag` column is restricted to the 5 canonical string values: `'ok'`, `'interpolated'`, `'missing'`, `'fault_suspect'`, `'night'`.
- **Foreign Key Integrity**: All relational tables enforce foreign keys pointing to `plants(plant_id)` with composite primary keys indexing time series.
- **Idempotency**: All DDL commands in `01_schema.sql` use `CREATE TABLE IF NOT EXISTS`.

---

## 2. Relational Schema Architecture (`db/init/01_schema.sql`)

### 1. `plants`
- Primary Key: `plant_id` (e.g., `'dka_01'`)
- Columns: `name`, `lat`, `lon`, `tz`, `capacity_kwp` (5.4), `inverter_max_kw` (5.0), `tilt` (20.0), `azimuth` (0.0).

### 2. `measurements`
- Composite Primary Key: `(ts_utc, plant_id)`
- Columns: `power_kw`, `poa_wm2`, `temp_air_c`, `temp_module_c`, `wind_speed_ms`, `quality_flag`.

### 3. `weather_forecast`
- Composite Primary Key: `(forecast_horizon_utc, as_of_utc, plant_id)`
- Columns: `poa_wm2`, `temp_air_c`, `wind_speed_10m`, `cloud_cover_pct`.

### 4. `model_forecast`
- Composite Primary Key: `(forecast_horizon_utc, as_of_utc, plant_id, model_version)`
- Columns: `raw_model_kw`, `clear_sky_kw`, `final_kw`, `guardrail_activated` (BOOLEAN), `rule_hit` (TEXT), `fallback_used` (BOOLEAN).

### 5. `plant_health_daily`
- Composite Primary Key: `(date, plant_id)`
- Columns: `pr_tc_daily`, `pr_smooth`, `soiling_loss_pct`, `status` (`'clean'`, `'soiled'`, `'critical_wash_needed'`, `'fault_suspect'`).

### 6. `alerts`
- Primary Key: `id SERIAL`
- Columns: `ts_utc`, `plant_id`, `severity` (`'INFO'`, `'WARNING'`, `'CRITICAL'`), `rule_type`, `message`, `acknowledged` (BOOLEAN).

---

## 3. Current Implementation Status

- **`01_schema.sql`**: Fully authored and verified at `db/init/01_schema.sql`.
- **Infrastructure**: Standalone PostgreSQL container definition and automated seed fixtures scheduled for Sprint 2.
