-- 0002_immutability.sql — inmutabilidad en el motor.
--
-- Tres capas: permisos (0005), estos triggers, y las pruebas de integración. Se mantienen
-- las tres porque un permiso puede cambiarse por accidente, y entonces el trigger deja un
-- error explícito en lugar de una escritura silenciosa.
--
-- Los triggers de SENTENCIA son los que hacen que la prohibición sea una propiedad de la
-- operación: un trigger de fila no se dispara cuando la operación no afecta a ninguna fila,
-- así que `DELETE FROM seal` sobre una tabla vacía tendría éxito. TRUNCATE, además, solo
-- admite disparo por sentencia: no existe TRUNCATE por fila.
--
-- Los triggers de FILA se conservan solo donde protegen campos concretos (asset).

CREATE OR REPLACE FUNCTION deny_statement() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION
        'CASTUO_APPEND_ONLY: % no admite % (tabla append-only)', TG_TABLE_NAME, TG_OP
        USING ERRCODE = 'restrict_violation';
END;
$$;

-- Todas las tablas append-only reciben el mismo triple candado.
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['detection', 'review', 'trace_event', 'seal',
                             'seal_anchor', 'asset_proposal', 'asset_status_event']
    LOOP
        EXECUTE format(
            'CREATE TRIGGER %I_no_update_stmt BEFORE UPDATE ON %I EXECUTE FUNCTION deny_statement()',
            t, t);
        EXECUTE format(
            'CREATE TRIGGER %I_no_delete_stmt BEFORE DELETE ON %I EXECUTE FUNCTION deny_statement()',
            t, t);
        EXECUTE format(
            'CREATE TRIGGER %I_no_truncate_stmt BEFORE TRUNCATE ON %I EXECUTE FUNCTION deny_statement()',
            t, t);
    END LOOP;
END
$$;

-- El activo es append-only en todos sus campos: el estado evoluciona por eventos, no por
-- UPDATE. Se conserva un trigger de FILA además del de sentencia porque nombra el campo
-- concreto que alguien intentó tocar, y ese detalle vale en una auditoría.
CREATE OR REPLACE FUNCTION asset_immutable() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE campo text;
BEGIN
    campo := CASE
        WHEN NEW.asset_id        IS DISTINCT FROM OLD.asset_id        THEN 'asset_id'
        WHEN NEW.asset_type      IS DISTINCT FROM OLD.asset_type      THEN 'asset_type'
        WHEN NEW.geometry        IS DISTINCT FROM OLD.geometry        THEN 'geometry'
        WHEN NEW.owner_ref       IS DISTINCT FROM OLD.owner_ref       THEN 'owner_ref'
        WHEN NEW.source_event_id IS DISTINCT FROM OLD.source_event_id THEN 'source_event_id'
        WHEN NEW.captured_at     IS DISTINCT FROM OLD.captured_at     THEN 'captured_at'
        WHEN NEW.created_at      IS DISTINCT FROM OLD.created_at      THEN 'created_at'
        WHEN NEW.schema_version  IS DISTINCT FROM OLD.schema_version  THEN 'schema_version'
        WHEN NEW.origen          IS DISTINCT FROM OLD.origen          THEN 'origen'
        WHEN NEW.initial_status  IS DISTINCT FROM OLD.initial_status  THEN 'initial_status'
        ELSE 'ninguno'
    END;
    RAISE EXCEPTION
        'CASTUO_IMMUTABLE_FIELD: asset.% no se puede modificar; el estado cambia con un evento en asset_status_event',
        campo USING ERRCODE = 'restrict_violation';
END;
$$;

CREATE TRIGGER asset_immutable_row      BEFORE UPDATE ON asset
    FOR EACH ROW EXECUTE FUNCTION asset_immutable();
CREATE TRIGGER asset_no_update_stmt     BEFORE UPDATE ON asset EXECUTE FUNCTION deny_statement();
CREATE TRIGGER asset_no_delete_stmt     BEFORE DELETE ON asset EXECUTE FUNCTION deny_statement();
CREATE TRIGGER asset_no_truncate_stmt   BEFORE TRUNCATE ON asset EXECUTE FUNCTION deny_statement();
