# SUBER UAV — núcleo de evidencia (pre-prototipo)

Capacidad de encuadre: `CAP-OFFLINE-FIRST-001`. Fase **exterior** a la arquitectura de
CASTÚO-SYSTEM (ADR-031 del repositorio de origen): entrega un paquete verificable, no una conexión.

## Estado (verificado en local, 2026-11-23)

- Núcleo de evidencia implementado y probado **con datos sintéticos**. Sin vuelos de ensayo,
  sin parcela ni autorización de vuelo.
- 284 pruebas pasan en local contra PostgreSQL 16 (`python -m pytest`).
- **No se afirma** producción, validación ni cierre de ningún gate de campo
  (`SUBER-G1…G3`). Los G1–G3 de SUBER UAV no son los `CS-G1…CS-G4` de `castuo-system`.

## Origen

Código importado desde el commit `b5f23f4` de `castuo-offline-field-operations`
(rama `archive/suber-uav-snapshot`), según la decisión de llevar la capacidad a este
repositorio. Única modificación: `docker-compose.test.yml` usa `POSTGRES_HOST_AUTH_METHOD: trust` en vez de
`POSTGRES_PASSWORD`, porque la contraseña literal incumple la regla de secretos de este repositorio
y además no funcionaba con el rol `castuo_app`, que no tiene contraseña. `pyproject.toml` declara además `fastapi` y, para pruebas, `httpx`, que el
origen usaba sin declararlos (el primer CI falló por eso; sin versiones mínimas, probado con
fastapi 0.162.2 y httpx 0.28.1). `src/`, `tests/`, `migrations/` y `scripts/` son idénticos al
origen (mismos blobs). Quedan **fuera** de esta importación todos los documentos (`docs/`, incluidas
`docs/publicaciones/`) y el `README` de origen.

## Ejecutar las pruebas

```
docker run -d --name suber-pg -e POSTGRES_USER=postgres -e POSTGRES_DB=castuo_test \
  -e POSTGRES_HOST_AUTH_METHOD=trust -p 5433:5432 postgres:16
docker exec suber-pg psql -U postgres -d castuo_test -c "CREATE ROLE castuo_app LOGIN;"
pip install -e ".[dev]"
CASTUO_PGPORT=5433 python -m pytest
```

Dos requisitos que el código de pruebas da por supuestos: el rol `castuo_app` debe existir
antes de la primera prueba (`tests/conftest.py` lo usa antes de aplicar las migraciones) y la
conexión local debe admitir acceso sin contraseña. Ambos se cubren en el flujo de CI.
