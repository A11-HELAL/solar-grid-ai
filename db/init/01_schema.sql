-- ==============================================================================
-- Solar-Grid AI v1.1 - Relational Schema (PostgreSQL 16)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS plants (
    plant_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    tz TEXT NOT NULL,
    capacity_kwp DOUBLE PRECISION NOT NULL,
    inverter_max_kw DOUBLE PRECISION NOT NULL,
    tilt DOUBLE PRECISION NOT NULL,
    azimuth DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS measurements (
    ts_utc TIMESTAMPTZ NOT NULL,
    plant_id TEXT NOT NULL REFERENCES plants(plant_id),
    power_kw DOUBLE PRECISION,
    poa_wm2 DOUBLE PRECISION,
    temp_air_c DOUBLE PRECISION,
    temp_module_c DOUBLE PRECISION,
    wind_speed_ms DOUBLE PRECISION,
    quality_flag TEXT NOT NULL,
    PRIMARY KEY (ts_utc, plant_id)
);

CREATE TABLE IF NOT EXISTS weather_forecast (
    forecast_horizon_utc TIMESTAMPTZ NOT NULL,
    as_of_utc TIMESTAMPTZ NOT NULL,
    plant_id TEXT NOT NULL REFERENCES plants(plant_id),
    poa_wm2 DOUBLE PRECISION NOT NULL,
    temp_air_c DOUBLE PRECISION NOT NULL,
    wind_speed_10m DOUBLE PRECISION NOT NULL,
    cloud_cover_pct DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (forecast_horizon_utc, as_of_utc, plant_id)
);

CREATE TABLE IF NOT EXISTS model_forecast (
    forecast_horizon_utc TIMESTAMPTZ NOT NULL,
    as_of_utc TIMESTAMPTZ NOT NULL,
    plant_id TEXT NOT NULL REFERENCES plants(plant_id),
    model_version TEXT NOT NULL,
    raw_model_kw DOUBLE PRECISION NOT NULL,
    clear_sky_kw DOUBLE PRECISION NOT NULL,
    final_kw DOUBLE PRECISION NOT NULL,
    guardrail_activated BOOLEAN NOT NULL DEFAULT FALSE,
    rule_hit TEXT,
    fallback_used BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (forecast_horizon_utc, as_of_utc, plant_id, model_version)
);

CREATE TABLE IF NOT EXISTS plant_health_daily (
    date DATE NOT NULL,
    plant_id TEXT NOT NULL REFERENCES plants(plant_id),
    pr_tc_daily DOUBLE PRECISION,
    pr_smooth DOUBLE PRECISION,
    soiling_loss_pct DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL,
    PRIMARY KEY (date, plant_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    ts_utc TIMESTAMPTZ NOT NULL,
    plant_id TEXT NOT NULL REFERENCES plants(plant_id),
    severity TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    message TEXT NOT NULL,
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE
);
