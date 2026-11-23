-- 0009_uav_mission.sql — la misión de vuelo y la observación, separadas de la detección.
--
-- Por qué esta migración existe (incoherencia 6 del estado maestro): hasta ahora `detection`
-- mezclaba dos cosas distintas —la observación derivada de un vuelo y la salida de un modelo
-- sobre esa observación—, de modo que reprocesar un vuelo con un modelo nuevo obligaba a
-- duplicar el dato bruto. Aquí se separan: `uav_observation` es el descriptor; `detection`
-- pasa a poder referenciarlo.
--
-- Sin la misión no hay serie temporal: dos observaciones del mismo árbol en fechas distintas
-- no son comparables si no se sabe con qué aeronave, qué carga útil, a qué altura y con qué
-- versión de extractor se produjeron. Es la entidad que hace posible el gate G1.
--
-- Escalera de carga útil (ADR-036): el tipo es cerrado a propósito. Subir un peldaño es una
-- decisión, no un detalle de configuración, y queda registrada en cada misión.

CREATE TYPE payload_t AS ENUM ('P0_rgb', 'P1_rgb_rtk', 'P2_multiespectral', 'P3_lidar');

CREATE TABLE uav_mission (
    mission_id        uuid PRIMARY KEY,
    forest_ref        text        NOT NULL CHECK (btrim(forest_ref) <> ''),
    aircraft          text        NOT NULL CHECK (btrim(aircraft) <> ''),
    payload           payload_t   NOT NULL,
    planned_agl_m     numeric(6,2) CHECK (planned_agl_m > 0),
    overlap_pct       numeric(5,2) CHECK (overlap_pct >= 0 AND overlap_pct <= 100),
    -- Referencia a la autorización de vuelo. NULL es legítimo mientras `origen` no sea
    -- 'real': un ensayo sintético no tiene autorización, y un vuelo real sin ella no debe
    -- poder registrarse. Lo comprueba el CHECK de más abajo.
    authorization_ref text,
    operator          uuid        NOT NULL,          -- actor opaco, nunca identidad
    extractor_version text        NOT NULL CHECK (btrim(extractor_version) <> ''),
    source_event_id   text        NOT NULL UNIQUE,   -- idempotencia de ingesta
    flown_at          timestamptz NOT NULL,
    created_at        timestamptz NOT NULL DEFAULT now(),
    schema_version    integer     NOT NULL,
    origen            origen_t    NOT NULL,
    CONSTRAINT mission_real_requires_authorization
        CHECK (origen <> 'real' OR (authorization_ref IS NOT NULL
                                    AND btrim(authorization_ref) <> ''))
);

CREATE INDEX uav_mission_forest_idx ON uav_mission (forest_ref, flown_at);

-- El descriptor por unidad observada. `asset_id` es nulo mientras la observación no se haya
-- vinculado a un árbol conocido: la reidentificación es precisamente lo que G1 tiene que
-- demostrar, y forzar el vínculo en la inserción daría por supuesto el resultado.
CREATE TABLE uav_observation (
    observation_id    uuid PRIMARY KEY,
    mission_id        uuid        NOT NULL REFERENCES uav_mission(mission_id),
    asset_id          uuid        REFERENCES asset(asset_id),
    unit_ref          text        NOT NULL CHECK (btrim(unit_ref) <> ''),
    descriptors       jsonb       NOT NULL,
    geometry          text,
    quality           numeric(6,5) NOT NULL CHECK (quality >= 0 AND quality <= 1),
    extractor_version text        NOT NULL CHECK (btrim(extractor_version) <> ''),
    observed_at       timestamptz NOT NULL,
    schema_version    integer     NOT NULL,
    origen            origen_t    NOT NULL,
    CONSTRAINT observation_unit_unique UNIQUE (mission_id, unit_ref)
);

CREATE INDEX uav_observation_asset_idx ON uav_observation (asset_id);

-- La detección pasa a poder apuntar a la observación de la que salió. Columna nueva y
-- anulable: las detecciones existentes siguen siendo válidas, y ninguna fila se reescribe.
ALTER TABLE detection
    ADD COLUMN observation_id uuid REFERENCES uav_observation(observation_id);

-- El mismo triple candado que el resto del asiento.
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['uav_mission', 'uav_observation']
    LOOP
        EXECUTE format(
            'CREATE TRIGGER %I_no_update_stmt BEFORE UPDATE ON %I '
            'EXECUTE FUNCTION deny_statement()', t, t);
        EXECUTE format(
            'CREATE TRIGGER %I_no_delete_stmt BEFORE DELETE ON %I '
            'EXECUTE FUNCTION deny_statement()', t, t);
        EXECUTE format(
            'CREATE TRIGGER %I_no_truncate_stmt BEFORE TRUNCATE ON %I '
            'EXECUTE FUNCTION deny_statement()', t, t);
    END LOOP;
END
$$;

GRANT SELECT, INSERT ON uav_mission, uav_observation TO castuo_app;
REVOKE UPDATE, DELETE, TRUNCATE ON uav_mission, uav_observation FROM castuo_app;
