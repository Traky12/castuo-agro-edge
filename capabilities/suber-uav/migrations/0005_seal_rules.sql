-- 0005_seal_rules.sql — la aceptación experta exige un sello local previo.
-- El CHECK de 0001 garantiza que seal_id no sea nulo; aquí se comprueba lo que un CHECK no
-- puede ver: que el sello exista, sea local, apunte a ESTA detección y sea anterior.

CREATE OR REPLACE FUNCTION review_seal_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    s_subject_type text;
    s_subject_id   uuid;
    s_kind         seal_kind_t;
    s_at           timestamptz;
BEGIN
    IF NEW.verdict <> 'accepted_by_expert' THEN
        RETURN NEW;   -- revisión preliminar o rechazo técnico: no exige sello
    END IF;

    -- Distinguir «sin sello» de «sello que no existe»: son dos fallos con causas distintas.
    IF NEW.seal_id IS NULL THEN
        RAISE EXCEPTION
            'CASTUO_SEAL: la aceptacion experta exige un sello local previo; no se ha indicado ninguno'
            USING ERRCODE = 'restrict_violation';
    END IF;

    SELECT subject_type, subject_id, seal_kind, sealed_at
      INTO s_subject_type, s_subject_id, s_kind, s_at
      FROM seal WHERE seal_id = NEW.seal_id;

    IF s_subject_id IS NULL THEN
        RAISE EXCEPTION 'CASTUO_SEAL: el sello % referenciado no existe', NEW.seal_id
            USING ERRCODE = 'restrict_violation';
    END IF;
    IF s_subject_type <> 'detection' OR s_subject_id <> NEW.detection_id THEN
        RAISE EXCEPTION
            'CASTUO_SEAL: el sello % no corresponde a la deteccion %', NEW.seal_id, NEW.detection_id
            USING ERRCODE = 'restrict_violation';
    END IF;
    IF s_at > NEW.reviewed_at THEN
        RAISE EXCEPTION
            'CASTUO_SEAL: el sello es posterior a la revision; el orden experto no puede preceder al sello'
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER review_seal_check BEFORE INSERT ON review
    FOR EACH ROW EXECUTE FUNCTION review_seal_guard();
