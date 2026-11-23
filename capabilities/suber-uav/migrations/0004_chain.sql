-- 0004_chain.sql — cadena por dispositivo sobre `event_hash`.
--
-- Un CHECK no puede mirar otra fila, así que la continuidad se valida en trigger: cada
-- evento debe apuntar al event_hash del último evento de SU dispositivo. Se encadena el
-- hash completo del evento y no solo el del payload, porque con el payload bastaría
-- cambiar actor, tipo u origen sin romper la continuidad.

CREATE OR REPLACE FUNCTION trace_chain_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    last_seq  bigint;
    last_hash bytea;
BEGIN
    SELECT sequence_no, event_hash INTO last_seq, last_hash
    FROM trace_event
    WHERE device_id = NEW.device_id
    ORDER BY sequence_no DESC
    LIMIT 1;

    IF last_seq IS NULL THEN
        IF NEW.sequence_no <> 1 THEN
            RAISE EXCEPTION
                'CASTUO_CHAIN: el primer evento del dispositivo % debe tener sequence_no = 1 (recibido %)',
                NEW.device_id, NEW.sequence_no USING ERRCODE = 'restrict_violation';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.sequence_no <> last_seq + 1 THEN
        RAISE EXCEPTION
            'CASTUO_CHAIN: hueco o salto en la cadena del dispositivo %; esperado %, recibido %',
            NEW.device_id, last_seq + 1, NEW.sequence_no USING ERRCODE = 'restrict_violation';
    END IF;

    IF NEW.previous_trace_hash IS DISTINCT FROM last_hash THEN
        RAISE EXCEPTION
            'CASTUO_CHAIN: previous_trace_hash no corresponde al event_hash del ultimo evento del dispositivo %',
            NEW.device_id USING ERRCODE = 'restrict_violation';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trace_chain_check BEFORE INSERT ON trace_event
    FOR EACH ROW EXECUTE FUNCTION trace_chain_guard();
