CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL PRIMARY KEY,
    mission_id VARCHAR(64) NOT NULL,
    timestamp_utc TIMESTAMP NOT NULL,
    uav_x DOUBLE PRECISION,
    uav_y DOUBLE PRECISION,
    bearing_deg DOUBLE PRECISION CHECK (bearing_deg >= 0 AND bearing_deg <= 360),
    quality_weight DOUBLE PRECISION CHECK (quality_weight > 0),
    is_valid BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_measurements_mission ON measurements(mission_id);

CREATE TABLE IF NOT EXISTS estimations (
    id SERIAL PRIMARY KEY,
    mission_id VARCHAR(64) NOT NULL,
    batch_no INTEGER NOT NULL,
    estimated_x DOUBLE PRECISION NOT NULL,
    estimated_y DOUBLE PRECISION NOT NULL,
    rmse DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_estimations_mission ON estimations(mission_id);

CREATE TABLE IF NOT EXISTS weapon_profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    category VARCHAR(64) NOT NULL,
    min_range_km DOUBLE PRECISION NOT NULL,
    max_range_km DOUBLE PRECISION NOT NULL,
    lethal_radius_m DOUBLE PRECISION NOT NULL,
    notes VARCHAR(255) NOT NULL DEFAULT ''
);
