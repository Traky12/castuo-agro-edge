-- 0008_devices.sql — identidad de los dispositivos que escriben.
--
-- La cadena de traza se particiona por dispositivo, así que la API necesita saber qué
-- dispositivo está escribiendo. La clave se guarda hasheada: una filtración de la base de
-- datos no debe entregar credenciales utilizables.
--
-- Autenticación mínima y deliberadamente provisional: sirve para que el prototipo
-- distinga dispositivos y registre quién escribió qué. NO es un esquema de autenticación
-- para producción — falta rotación, caducidad y revocación auditada.
-- [PENDIENTE: esquema de credenciales de producción]

CREATE TABLE device (
    device_id      uuid PRIMARY KEY,
    label          text        NOT NULL,
    api_key_hash   bytea       NOT NULL UNIQUE CHECK (octet_length(api_key_hash) = 32),
    enrolled_at    timestamptz NOT NULL DEFAULT now(),
    revoked_at     timestamptz,
    schema_version integer     NOT NULL,
    origen         origen_t    NOT NULL
);
CREATE INDEX device_active_idx ON device (api_key_hash) WHERE revoked_at IS NULL;

-- La revocación es lo único mutable, y solo en un sentido: revocar, nunca "des-revocar".
CREATE OR REPLACE FUNCTION device_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'CASTUO_APPEND_ONLY: device no admite DELETE; revoca en su lugar'
            USING ERRCODE = 'restrict_violation';
    END IF;
    IF NEW.device_id    IS DISTINCT FROM OLD.device_id
    OR NEW.api_key_hash IS DISTINCT FROM OLD.api_key_hash
    OR NEW.enrolled_at  IS DISTINCT FROM OLD.enrolled_at
    OR NEW.origen       IS DISTINCT FROM OLD.origen THEN
        RAISE EXCEPTION 'CASTUO_IMMUTABLE_FIELD: en device solo puede cambiar revoked_at'
            USING ERRCODE = 'restrict_violation';
    END IF;
    IF OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS NULL THEN
        RAISE EXCEPTION 'CASTUO_DEVICE: un dispositivo revocado no se puede reactivar'
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER device_guard_row     BEFORE UPDATE OR DELETE ON device
    FOR EACH ROW EXECUTE FUNCTION device_guard();
CREATE TRIGGER device_no_truncate   BEFORE TRUNCATE ON device EXECUTE FUNCTION deny_statement();

GRANT SELECT, INSERT ON device TO castuo_app;
GRANT UPDATE (revoked_at) ON device TO castuo_app;
