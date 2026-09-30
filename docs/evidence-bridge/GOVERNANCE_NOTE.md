# Evidence Bridge (EB-POC-001) — nota de gobernanza

## Qué es esto

`evidence_bridge/` es un PoC técnico interno y aislado que explora si CASTÚO-SYSTEM
puede capturar, dar procedencia, y exportar como evidencia revisable una desviación
de cultivo — sin sustituir ningún SaaS de cultivo ni QMS existente de un tercero.

## Por qué vive en `castuo-agro-edge` y no en otro repo

Antes de escribir código se revisó el ecosistema para no crear arquitectura paralela
donde ya existiera una capa reutilizable (principio de gobernanza CASTÚO-SYSTEM):

- **`Castuo-system`** ya tiene un patrón de hash+manifest+procedencia (SEV,
  `scripts/evidence/generate_sev.py`; Digital Thread,
  `docs/evidence/DIGITAL-THREAD.md`) — pero cubre *commits de CI/CD y documentos*,
  no telemetría de cultivo ni desviaciones de QMS. Los gates de campo G2/G3 siguen
  `Pendiente`: este PoC no depende de ellos ni afirma cerrarlos.
- **`Cast-o`**, **`castuo-evidence`**, **`castuo-e3-001`** son un motor de testing y
  paquetes de evidencia **congelados** de un benchmark puntual (S-001A,
  `PROMOTION: BLOCKED`) — no son infraestructura operativa de ingesta.
- **`castuo-agro-edge`** es el repo edge/telemetría canónico (frente a
  `castuo-offline-field-operations`, sin código): ya tiene cola SQLite offline
  (`gateway/buffering/store.py`), gateway MQTT y un stub de sincronización
  (`gateway/sync/upstream.py`). Es la base más cercana a lo que este PoC necesita
  (continuidad offline, telemetría), así que se construye aquí, en un paquete
  aislado (`evidence_bridge/`) que no toca `telemetry_queue` ni el daemon
  `BufferDB`/`SyncWorker` de `gateway/mqtt/`.

## Estado de madurez

Según la escalera de `docs/CASTUO_ARCHITECTURE_GOVERNANCE.md`
(`DOCUMENTED → IMPLEMENTED → TESTED → VALIDATED → PILOT → OPERATIONAL`):

- Esquemas, fixtures, ingesta, validación, procedencia (hash) y continuidad offline:
  **IMPLEMENTED + TESTED** (tests sintéticos locales).
- Reconciliación, timeline, exportación de Evidence Pack y verificación
  independiente: **DOCUMENTED** solamente (stubs, iteración 2).
- **Nada de esto está `VALIDATED`, `PILOT` ni `OPERATIONAL`.** No hay dato real de
  ningún cliente, no hay integración con un SaaS o QMS real, no hay validación
  GxP/GMP. Ver `SCOPE_AND_EXCLUSIONS.md`.

## Decisión pendiente

La fusión/promoción de esta rama es una decisión humana, no automática — usar
`decision-template.md` para registrar `NO_FIT` / `GAP_CONFIRMED` / `PILOT_AUTHORIZED`.
