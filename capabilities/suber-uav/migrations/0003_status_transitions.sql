-- 0003_status_transitions.sql — transiciones de estado declaradas.
--
-- El estado no es libre: solo se admiten los saltos que el dominio reconoce, y el evento
-- tiene que partir del estado vigente. Sin esta comprobación, dos eventos concurrentes
-- podrían dejar el activo en un estado que nadie decidió.

CREATE OR REPLACE FUNCTION asset_status_transition_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    vigente     asset_status_t;
    ultima_seq  bigint;
    valido      boolean;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('asset_status'), hashtext(NEW.asset_id::text));

    SELECT max(e.sequence_no) INTO ultima_seq
      FROM asset_status_event e WHERE e.asset_id = NEW.asset_id;

    SELECT COALESCE(
        (SELECT e.to_status FROM asset_status_event e
          WHERE e.asset_id = NEW.asset_id
          ORDER BY e.sequence_no DESC LIMIT 1),
        a.initial_status)
      INTO vigente
      FROM asset a WHERE a.asset_id = NEW.asset_id;

    IF vigente IS NULL THEN
        RAISE EXCEPTION 'CASTUO_STATUS: el activo % no existe', NEW.asset_id
            USING ERRCODE = 'restrict_violation';
    END IF;

    IF NEW.sequence_no <> COALESCE(ultima_seq, 0) + 1 THEN
        RAISE EXCEPTION
            'CASTUO_STATUS: hueco o salto en la secuencia del activo %; esperado %, recibido %',
            NEW.asset_id, COALESCE(ultima_seq, 0) + 1, NEW.sequence_no
            USING ERRCODE = 'restrict_violation';
    END IF;

    IF NEW.from_status IS DISTINCT FROM vigente THEN
        RAISE EXCEPTION
            'CASTUO_STATUS: el evento parte de % pero el estado vigente es %',
            COALESCE(NEW.from_status::text, 'NULL'), vigente
            USING ERRCODE = 'restrict_violation';
    END IF;

    -- Transiciones declaradas. Cualquier otra se rechaza, incluido quedarse igual.
    valido := (NEW.from_status = 'detectado' AND NEW.to_status IN ('validado', 'descartado'))
           OR (NEW.from_status = 'validado'  AND NEW.to_status = 'descartado')
           OR (NEW.from_status = 'pendiente' AND NEW.to_status IN ('detectado', 'descartado'));

    IF NOT valido THEN
        RAISE EXCEPTION
            'CASTUO_STATUS: transicion no declarada % -> %', NEW.from_status, NEW.to_status
            USING ERRCODE = 'restrict_violation';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER asset_status_transition_check BEFORE INSERT ON asset_status_event
    FOR EACH ROW EXECUTE FUNCTION asset_status_transition_guard();
