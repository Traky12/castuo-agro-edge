-- 0007_contrast.sql — ordenación y contraste ciego.
--
-- Es el núcleo del preprototipo: el sistema produce un orden, se congela y se sella, y
-- SOLO ENTONCES puede entrar el orden del corchego experto. El umbral de aceptación se
-- registra en el protocolo ANTES de que exista ningún dato, porque fijarlo después es
-- elegir el listón que uno acaba de saltar.

CREATE TYPE unit_kind_t   AS ENUM ('arbol', 'rodal', 'unidad_pila');
CREATE TYPE metric_t      AS ENUM ('spearman', 'kendall_tau_b');
CREATE TYPE verdict_g2_t  AS ENUM ('supera', 'no_supera');

-- ------------------------------------------------------------------- protocolo
CREATE TABLE contrast_protocol (
    protocol_id     uuid PRIMARY KEY,
    scope_ref       text        NOT NULL,          -- parcela o conjunto sobre el que se ordena
    unit_kind       unit_kind_t NOT NULL,          -- decisión A-01
    metric          metric_t    NOT NULL,
    threshold       numeric(6,5) NOT NULL CHECK (threshold >= -1 AND threshold <= 1),
    registered_by   uuid        NOT NULL,
    registered_at   timestamptz NOT NULL DEFAULT now(),
    schema_version  integer     NOT NULL,
    origen          origen_t    NOT NULL
);
CREATE INDEX contrast_protocol_scope_idx ON contrast_protocol (scope_ref);

-- ------------------------------------------------------------------- orden del sistema
CREATE TABLE ranking (
    ranking_id      uuid PRIMARY KEY,
    protocol_id     uuid        NOT NULL REFERENCES contrast_protocol(protocol_id),
    model_id        text        NOT NULL CHECK (btrim(model_id) <> ''),
    model_version   text        NOT NULL CHECK (btrim(model_version) <> ''),
    params          jsonb       NOT NULL DEFAULT '{}'::jsonb,
    content_hash    bytea       NOT NULL CHECK (octet_length(content_hash) = 32),
    created_at      timestamptz NOT NULL DEFAULT now(),
    schema_version  integer     NOT NULL,
    origen          origen_t    NOT NULL
);
CREATE INDEX ranking_protocol_idx ON ranking (protocol_id);

CREATE TABLE ranking_item (
    ranking_item_id uuid PRIMARY KEY,
    ranking_id      uuid         NOT NULL REFERENCES ranking(ranking_id),
    unit_ref        text         NOT NULL,
    position        integer      NOT NULL CHECK (position >= 1),
    score           numeric(12,6) NOT NULL,
    schema_version  integer      NOT NULL,
    origen          origen_t     NOT NULL,
    CONSTRAINT ranking_item_unit_unique     UNIQUE (ranking_id, unit_ref),
    CONSTRAINT ranking_item_position_unique UNIQUE (ranking_id, position)
);

-- ------------------------------------------------------------------- orden del experto
CREATE TABLE expert_ranking (
    expert_ranking_id uuid PRIMARY KEY,
    ranking_id        uuid        NOT NULL REFERENCES ranking(ranking_id),
    actor             uuid        NOT NULL,        -- identidad opaca
    created_at        timestamptz NOT NULL DEFAULT now(),
    schema_version    integer     NOT NULL,
    origen            origen_t    NOT NULL,
    CONSTRAINT expert_ranking_once UNIQUE (ranking_id, actor)
);

CREATE TABLE expert_ranking_item (
    expert_item_id    uuid PRIMARY KEY,
    expert_ranking_id uuid    NOT NULL REFERENCES expert_ranking(expert_ranking_id),
    unit_ref          text    NOT NULL,
    position          integer NOT NULL CHECK (position >= 1),
    schema_version    integer NOT NULL,
    origen            origen_t NOT NULL,
    CONSTRAINT expert_item_unit_unique     UNIQUE (expert_ranking_id, unit_ref),
    CONSTRAINT expert_item_position_unique UNIQUE (expert_ranking_id, position)
);

-- ------------------------------------------------------------------- concordancia
CREATE TABLE concordance (
    concordance_id    uuid PRIMARY KEY,
    ranking_id        uuid         NOT NULL REFERENCES ranking(ranking_id),
    expert_ranking_id uuid         NOT NULL REFERENCES expert_ranking(expert_ranking_id),
    metric            metric_t     NOT NULL,
    metric_version    text         NOT NULL,
    value             numeric(9,6) NOT NULL CHECK (value >= -1 AND value <= 1),
    threshold_applied numeric(6,5) NOT NULL,       -- copiado del protocolo, no del llamante
    verdict           verdict_g2_t NOT NULL,
    computed_at       timestamptz  NOT NULL DEFAULT now(),
    schema_version    integer      NOT NULL,
    origen            origen_t     NOT NULL,
    CONSTRAINT concordance_once UNIQUE (ranking_id, expert_ranking_id, metric)
);

-- ------------------------------------------------------------------- el muro
-- El orden del experto no puede entrar antes de que el orden del sistema esté sellado.
-- Es la propiedad que convierte el contraste ciego en algo comprobable por un tercero en
-- lugar de en una afirmación de método.
CREATE OR REPLACE FUNCTION expert_ranking_needs_seal() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE sellado timestamptz;
BEGIN
    SELECT min(s.sealed_at) INTO sellado
      FROM seal s
     WHERE s.subject_type = 'ranking' AND s.subject_id = NEW.ranking_id
       AND s.seal_kind = 'local';

    IF sellado IS NULL THEN
        RAISE EXCEPTION
            'CASTUO_BLIND: el orden del experto no puede cargarse antes de sellar el ranking %',
            NEW.ranking_id USING ERRCODE = 'restrict_violation';
    END IF;
    IF sellado > NEW.created_at THEN
        RAISE EXCEPTION
            'CASTUO_BLIND: el sello del ranking % es posterior a la carga del orden experto',
            NEW.ranking_id USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER expert_ranking_blind_check BEFORE INSERT ON expert_ranking
    FOR EACH ROW EXECUTE FUNCTION expert_ranking_needs_seal();

-- Las cinco tablas son append-only, con el mismo triple candado que el resto.
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['contrast_protocol', 'ranking', 'ranking_item',
                             'expert_ranking', 'expert_ranking_item', 'concordance']
    LOOP
        EXECUTE format('CREATE TRIGGER %I_no_update_stmt BEFORE UPDATE ON %I EXECUTE FUNCTION deny_statement()', t, t);
        EXECUTE format('CREATE TRIGGER %I_no_delete_stmt BEFORE DELETE ON %I EXECUTE FUNCTION deny_statement()', t, t);
        EXECUTE format('CREATE TRIGGER %I_no_truncate_stmt BEFORE TRUNCATE ON %I EXECUTE FUNCTION deny_statement()', t, t);
        EXECUTE format('GRANT SELECT, INSERT ON %I TO castuo_app', t);
    END LOOP;
END
$$;
