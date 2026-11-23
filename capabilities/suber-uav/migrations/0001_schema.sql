-- 0001_schema.sql — entidades del Vertical Slice 01.
--
-- Todo el modelo es append-only, incluido el activo: el estado no se reescribe, se
-- registra como evento. Eso deja al rol de aplicación sin UPDATE en ninguna tabla.
-- Geometría como WKT en texto: PostGIS queda fuera de este slice. [PENDIENTE: PostGIS]

CREATE TYPE origen_t       AS ENUM ('real', 'simulado', 'historico');
CREATE TYPE asset_status_t AS ENUM ('detectado', 'validado', 'descartado', 'pendiente');
CREATE TYPE asset_type_t   AS ENUM ('parcela', 'arbol', 'vuelo', 'imagen', 'sensor',
                                    'muestra', 'documento');
CREATE TYPE verdict_t      AS ENUM ('accepted_by_expert', 'rejected', 'preliminary',
                                    'technical_reject');
CREATE TYPE review_type_t  AS ENUM ('expert', 'preliminary', 'technical');
CREATE TYPE seal_kind_t    AS ENUM ('local');

-- ---------------------------------------------------------------- inventario
CREATE TABLE asset (
    asset_id        uuid PRIMARY KEY,
    asset_type      asset_type_t   NOT NULL,
    geometry        text,
    owner_ref       uuid,                            -- referencia seudonimizada, jamás identidad
    initial_status  asset_status_t NOT NULL DEFAULT 'detectado',
    source_event_id text           NOT NULL UNIQUE,  -- idempotencia de ingesta
    captured_at     timestamptz    NOT NULL,
    created_at      timestamptz    NOT NULL DEFAULT now(),
    schema_version  integer        NOT NULL,
    origen          origen_t       NOT NULL
);

-- El estado del activo evoluciona por eventos, no por UPDATE. Así queda registrado quién
-- lo cambió y cuándo, que en un sistema de evidencia es parte del producto.
-- `sequence_no` y no la hora: now() devuelve la hora de la TRANSACCIÓN, así que dos
-- transiciones escritas en la misma transacción comparten timestamp y el orden quedaría
-- decidido por el UUID, es decir al azar. El estado vigente de un activo no puede depender
-- de eso.
CREATE TABLE asset_status_event (
    status_event_id uuid PRIMARY KEY,
    asset_id        uuid           NOT NULL REFERENCES asset(asset_id),
    sequence_no     bigint         NOT NULL CHECK (sequence_no >= 1),
    from_status     asset_status_t,                  -- NULL solo en el evento inicial
    to_status       asset_status_t NOT NULL,
    actor           uuid           NOT NULL,
    reason          text,
    occurred_at     timestamptz    NOT NULL DEFAULT now(),
    schema_version  integer        NOT NULL,
    origen          origen_t       NOT NULL,
    CONSTRAINT asset_status_sequence_unique UNIQUE (asset_id, sequence_no)
);
CREATE INDEX asset_status_event_asset_idx ON asset_status_event (asset_id, sequence_no);

-- Estado vigente como proyección: se consulta, no se almacena.
CREATE VIEW asset_current AS
SELECT a.*,
       COALESCE(
           (SELECT e.to_status FROM asset_status_event e
             WHERE e.asset_id = a.asset_id
             ORDER BY e.sequence_no DESC LIMIT 1),
           a.initial_status
       ) AS status
FROM asset a;

-- ---------------------------------------------------------------- detección
CREATE TABLE detection (
    detection_id   uuid PRIMARY KEY,
    asset_id       uuid REFERENCES asset(asset_id),   -- nulo al proponer un activo (C-1)
    evidence_id    text         NOT NULL,
    model_id       text         NOT NULL CHECK (btrim(model_id) <> ''),
    model_version  text         NOT NULL CHECK (btrim(model_version) <> ''),
    label          text         NOT NULL,
    confidence     numeric(6,5) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    geometry       text,
    params         jsonb        NOT NULL DEFAULT '{}'::jsonb,
    input_hash     bytea        NOT NULL CHECK (octet_length(input_hash) = 32),
    result_hash    bytea        NOT NULL CHECK (octet_length(result_hash) = 32),
    detected_at    timestamptz  NOT NULL DEFAULT now(),
    schema_version integer      NOT NULL,
    origen         origen_t     NOT NULL
);
CREATE INDEX detection_asset_idx    ON detection (asset_id);
CREATE INDEX detection_evidence_idx ON detection (evidence_id);

-- Vínculo detección -> activo propuesto. Vive aparte porque la detección no se reescribe.
CREATE TABLE asset_proposal (
    proposal_id    uuid PRIMARY KEY,
    detection_id   uuid        NOT NULL REFERENCES detection(detection_id),
    asset_id       uuid        NOT NULL REFERENCES asset(asset_id),
    proposed_at    timestamptz NOT NULL DEFAULT now(),
    schema_version integer     NOT NULL,
    origen         origen_t    NOT NULL,
    CONSTRAINT asset_proposal_unique UNIQUE (detection_id, asset_id)
);
CREATE INDEX asset_proposal_detection_idx ON asset_proposal (detection_id);
CREATE INDEX asset_proposal_asset_idx     ON asset_proposal (asset_id);

-- ---------------------------------------------------------------- sello
CREATE TABLE seal (
    seal_id        uuid PRIMARY KEY,
    subject_type   text        NOT NULL,
    subject_id     uuid        NOT NULL,
    canonical_hash bytea       NOT NULL CHECK (octet_length(canonical_hash) = 32),
    seal_kind      seal_kind_t NOT NULL DEFAULT 'local',
    sealed_at      timestamptz NOT NULL DEFAULT now(),
    schema_version integer     NOT NULL,
    origen         origen_t    NOT NULL
);
CREATE INDEX seal_subject_idx ON seal (subject_type, subject_id);

-- El token RFC 3161 ancla un hash existente; no modifica lo sellado. Por eso vive en su
-- propia tabla append-only y no como columna que habría que rellenar después.
CREATE TABLE seal_anchor (
    anchor_id      uuid PRIMARY KEY,
    seal_id        uuid        NOT NULL REFERENCES seal(seal_id),
    tsa_token      bytea       NOT NULL,
    authority      text        NOT NULL,
    anchored_at    timestamptz NOT NULL DEFAULT now(),
    schema_version integer     NOT NULL,
    origen         origen_t    NOT NULL
);
CREATE INDEX seal_anchor_seal_idx ON seal_anchor (seal_id);

-- ---------------------------------------------------------------- revisión
CREATE TABLE review (
    review_id      uuid PRIMARY KEY,
    detection_id   uuid          NOT NULL REFERENCES detection(detection_id),
    verdict        verdict_t     NOT NULL,
    review_type    review_type_t NOT NULL,
    actor          uuid          NOT NULL,           -- identidad opaca (ADR-012)
    reviewed_at    timestamptz   NOT NULL DEFAULT now(),
    seal_id        uuid          REFERENCES seal(seal_id),
    schema_version integer       NOT NULL,
    origen         origen_t      NOT NULL,
    CONSTRAINT review_expert_requires_seal
        CHECK (verdict <> 'accepted_by_expert' OR seal_id IS NOT NULL)
);
CREATE INDEX review_detection_idx ON review (detection_id);

-- ---------------------------------------------------------------- trazabilidad
-- La cadena encadena `event_hash`, no `payload_hash`: encadenar solo el payload dejaría
-- alterar actor, tipo de evento u origen sin romper la continuidad.
CREATE TABLE trace_event (
    trace_id            uuid PRIMARY KEY,
    device_id           uuid        NOT NULL,
    entity_type         text        NOT NULL,
    entity_id           uuid        NOT NULL,
    event_type          text        NOT NULL,
    actor               uuid        NOT NULL,
    sequence_no         bigint      NOT NULL CHECK (sequence_no >= 1),
    occurred_at         timestamptz NOT NULL DEFAULT now(),
    payload_hash        bytea       NOT NULL CHECK (octet_length(payload_hash) = 32),
    event_hash          bytea       NOT NULL UNIQUE CHECK (octet_length(event_hash) = 32),
    previous_trace_hash bytea       CHECK (previous_trace_hash IS NULL
                                        OR octet_length(previous_trace_hash) = 32),
    schema_version      integer     NOT NULL,
    origen              origen_t    NOT NULL,
    CONSTRAINT trace_device_sequence_unique UNIQUE (device_id, sequence_no),
    CONSTRAINT trace_first_event_has_no_previous
        CHECK ((sequence_no = 1) = (previous_trace_hash IS NULL))
);
CREATE INDEX trace_entity_idx ON trace_event (entity_type, entity_id);
