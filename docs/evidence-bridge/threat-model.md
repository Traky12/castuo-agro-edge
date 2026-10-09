# Evidence Bridge (EB-POC-001) — modelo de amenazas

| # | Amenaza | Mitigación implementada ahora | Pendiente (iteración 2) |
|---|---------|-------------------------------|-------------------------|
| 1 | Payload alterado tras la ingesta | `provenance.py::verify_event_hash` recalcula el hash canónico y detecta cualquier cambio | Verificación independiente de todo un Evidence Pack exportado (`verify_pack.py`) |
| 2 | Evento duplicado (reenvío del origen) | Ninguna — se registra tal cual, detección es responsabilidad de `reconcile.py` | Detección por `source_system` + `source_event_id` |
| 3 | Evento retrasado | Se conserva `occurred_at` vs `received_at` sin fusionarlos | Clasificación por umbral de retraso |
| 4 | Hueco/pérdida en la secuencia | Ninguna — se registra tal cual | Detección de huecos por `sequence_number` cuando esté disponible |
| 5 | JSON malformado o campo obligatorio ausente | `bridge/validate.py` rechaza contra JSON Schema; `ingest.py` nunca completa un campo por inferencia | — |
| 6 | Caída de red / origen no disponible | `offline/queue_adapter.py` persiste localmente; reintento idempotente (`INSERT OR IGNORE` por `event_id`) | Reconciliación de conflictos tras reconexión prolongada |
| 7 | Revisión no autorizada de una desviación | Fuera de alcance de este PoC (no hay modelo de roles) | Requiere identidad/rol antes de cualquier uso más allá de PoC interno |
| 8 | Fuga de secretos en fixtures/docs | Todos los datasets son sintéticos, sin credenciales ni datos de cliente/CTAEX (revisado antes de cada commit) | — |
| 9 | Colisión con las colas offline existentes del repo | `evidence_bridge_events` es una tabla propia, nunca toca `telemetry_queue` ni `BufferDB` | — |
