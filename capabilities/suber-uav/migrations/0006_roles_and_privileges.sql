-- 0006_roles_and_privileges.sql — capa 1 de la inmutabilidad: permisos.
--
-- El rol de aplicación no tiene UPDATE ni DELETE en NINGUNA tabla. Es posible porque el
-- estado del activo dejó de ser una columna mutable y pasó a ser un evento: sin esa
-- decisión, aquí quedaría un GRANT UPDATE abierto que alguien acabaría ampliando.
-- La contraseña se inyecta fuera del control de versiones. [PENDIENTE: gestión de secretos]

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'castuo_app') THEN
        CREATE ROLE castuo_app LOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO castuo_app;

GRANT SELECT, INSERT ON asset, asset_status_event, detection, asset_proposal,
                         review, seal, seal_anchor, trace_event TO castuo_app;
GRANT SELECT ON asset_current TO castuo_app;

REVOKE UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM castuo_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE UPDATE, DELETE, TRUNCATE ON TABLES FROM castuo_app;
