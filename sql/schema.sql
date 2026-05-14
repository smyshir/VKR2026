-- PostgreSQL physical schema for VKR2026
-- Combines current running prototype tables + normalized logical model from practice report.

BEGIN;

-- =========================
-- Reference dictionaries
-- =========================
CREATE TABLE IF NOT EXISTS roles (
    role_id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(role_id) ON UPDATE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS equipment_types (
    equipment_type_id BIGSERIAL PRIMARY KEY,
    equipment_type_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS direction_finders (
    direction_finder_id BIGSERIAL PRIMARY KEY,
    equipment_type_id BIGINT NOT NULL REFERENCES equipment_types(equipment_type_id) ON UPDATE CASCADE,
    finder_name VARCHAR(120) NOT NULL,
    frequency_per_sec NUMERIC(10,3),
    average_error NUMERIC(12,6),
    description TEXT,
    UNIQUE (equipment_type_id, finder_name)
);

CREATE TABLE IF NOT EXISTS uavs (
    uav_id BIGSERIAL PRIMARY KEY,
    uav_name VARCHAR(120) NOT NULL UNIQUE,
    uav_type VARCHAR(120),
    avg_speed NUMERIC(10,3),
    max_speed NUMERIC(10,3),
    description TEXT
);

CREATE TABLE IF NOT EXISTS scenario_types (
    scenario_id BIGSERIAL PRIMARY KEY,
    scenario_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS destruction_means (
    destruction_means_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    type VARCHAR(120) NOT NULL,
    min_range NUMERIC(10,3) NOT NULL,
    max_range NUMERIC(10,3) NOT NULL,
    effective_radius NUMERIC(10,3) NOT NULL,
    description TEXT
);

-- =========================
-- Operational datasets
-- =========================
CREATE TABLE IF NOT EXISTS input_data_sets (
    dataset_id BIGSERIAL PRIMARY KEY,
    uav_id BIGINT NOT NULL REFERENCES uavs(uav_id) ON UPDATE CASCADE,
    scenario_id BIGINT NOT NULL REFERENCES scenario_types(scenario_id) ON UPDATE CASCADE,
    direction_finder_id BIGINT NOT NULL REFERENCES direction_finders(direction_finder_id) ON UPDATE CASCADE,
    dataset_name VARCHAR(160) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    description TEXT,
    UNIQUE (dataset_name, created_at)
);

CREATE TABLE IF NOT EXISTS raw_measurements (
    raw_measurement_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL REFERENCES input_data_sets(dataset_id) ON DELETE CASCADE,
    x_bpla NUMERIC(14,6),
    y_bpla NUMERIC(14,6),
    bearing_b NUMERIC(10,6),
    measurement_time TIMESTAMP NOT NULL,
    quality_raw NUMERIC(10,6),
    CHECK (bearing_b IS NULL OR (bearing_b >= 0 AND bearing_b <= 360)),
    CHECK (quality_raw IS NULL OR quality_raw > 0)
);
CREATE INDEX IF NOT EXISTS idx_raw_measurements_dataset_time ON raw_measurements(dataset_id, measurement_time);

CREATE TABLE IF NOT EXISTS processed_measurements (
    processed_measurement_id BIGSERIAL PRIMARY KEY,
    raw_measurement_id BIGINT NOT NULL UNIQUE REFERENCES raw_measurements(raw_measurement_id) ON DELETE CASCADE,
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    weight NUMERIC(10,6),
    filter_comment TEXT,
    CHECK (weight IS NULL OR weight > 0)
);

CREATE TABLE IF NOT EXISTS aggregated_results (
    aggregated_result_id BIGSERIAL PRIMARY KEY,
    destruction_means_id BIGINT REFERENCES destruction_means(destruction_means_id) ON UPDATE CASCADE,
    x_center NUMERIC(14,6) NOT NULL,
    y_center NUMERIC(14,6) NOT NULL,
    scatter_radius NUMERIC(14,6) NOT NULL,
    point_count INTEGER NOT NULL CHECK (point_count >= 0)
);

CREATE TABLE IF NOT EXISTS calculation_runs (
    calculation_run_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL REFERENCES input_data_sets(dataset_id) ON UPDATE CASCADE,
    scenario_id BIGINT NOT NULL REFERENCES scenario_types(scenario_id) ON UPDATE CASCADE,
    grid_segments_x INTEGER NOT NULL CHECK (grid_segments_x BETWEEN 10 AND 100),
    grid_segments_y INTEGER NOT NULL CHECK (grid_segments_y BETWEEN 10 AND 100),
    run_datetime TIMESTAMP NOT NULL DEFAULT NOW(),
    comment TEXT
);

CREATE TABLE IF NOT EXISTS calculation_results (
    calculation_result_id BIGSERIAL PRIMARY KEY,
    calculation_run_id BIGINT NOT NULL REFERENCES calculation_runs(calculation_run_id) ON DELETE CASCADE,
    aggregated_result_id BIGINT REFERENCES aggregated_results(aggregated_result_id) ON DELETE SET NULL,
    x_result NUMERIC(14,6) NOT NULL,
    y_result NUMERIC(14,6) NOT NULL,
    residual_min NUMERIC(12,6) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_calc_results_run ON calculation_results(calculation_run_id);

CREATE TABLE IF NOT EXISTS experimental_runs (
    experimental_run_id BIGSERIAL PRIMARY KEY,
    scenario_id BIGINT NOT NULL REFERENCES scenario_types(scenario_id) ON UPDATE CASCADE,
    dataset_id BIGINT NOT NULL REFERENCES input_data_sets(dataset_id) ON UPDATE CASCADE,
    calculation_run_id BIGINT NOT NULL REFERENCES calculation_runs(calculation_run_id) ON DELETE CASCADE,
    reference_x NUMERIC(14,6) NOT NULL,
    reference_y NUMERIC(14,6) NOT NULL,
    sigma NUMERIC(12,6),
    comment TEXT
);

-- =========================
-- Compatibility tables for current backend code
-- =========================
CREATE TABLE IF NOT EXISTS measurements (
    id BIGSERIAL PRIMARY KEY,
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
    id BIGSERIAL PRIMARY KEY,
    mission_id VARCHAR(64) NOT NULL,
    batch_no INTEGER NOT NULL,
    estimated_x DOUBLE PRECISION NOT NULL,
    estimated_y DOUBLE PRECISION NOT NULL,
    rmse DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_estimations_mission ON estimations(mission_id);

CREATE TABLE IF NOT EXISTS weapon_profiles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    category VARCHAR(64) NOT NULL,
    min_range_km DOUBLE PRECISION NOT NULL,
    max_range_km DOUBLE PRECISION NOT NULL,
    lethal_radius_m DOUBLE PRECISION NOT NULL,
    notes VARCHAR(255) NOT NULL DEFAULT ''
);

-- Seed data
INSERT INTO roles (role_name, description)
VALUES ('Администратор','Управление справочниками и пользователями'), ('Оператор','Загрузка и запуск расчётов'), ('Аналитик','Анализ результатов')
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO scenario_types (scenario_name, description)
VALUES ('practical','Практический сценарий'), ('experimental','Экспериментальный сценарий')
ON CONFLICT (scenario_name) DO NOTHING;

INSERT INTO destruction_means (name, type, min_range, max_range, effective_radius, description)
VALUES
('РСЗО "Град"','РСЗО',5,20,15,'Средство площадного поражения'),
('ОФС 122мм','Артиллерия',3,15,12,'Фугасный снаряд'),
('ОФС 152мм','Артиллерия',5,24,20,'Фугасный снаряд увеличенного поражения')
ON CONFLICT (name) DO NOTHING;

COMMIT;
