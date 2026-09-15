EVIDENCE ID: EB-POC-001
STATUS: EXPERIMENTAL / INTERNAL ONLY

# IN SCOPE

- Dataset sintético de telemetría (6 escenarios: normal, desviación ambiental,
  duplicado, retrasado, corrupto/malformado, hueco de secuencia).
- Validación de esquema (JSON Schema, 4 tipos: evento, desviación, acción de
  revisión, manifiesto de evidencia).
- Procedencia por campo (`PROVIDED` / `GENERATED_BY_BRIDGE` / `DERIVED` /
  `UNKNOWN` / `NOT_AVAILABLE`) y hash canónico encadenado (sha256) por evento.
- Continuidad offline: cola local aislada (`evidence_bridge/offline/queue_adapter.py`),
  simulación de caída de conexión y reintento idempotente tras reconexión.

# OUT OF SCOPE (esta iteración)

- Reconciliación real (duplicados/huecos/retrasos) — stub en `bridge/reconcile.py`.
- Timeline de desviación completo — stub en `bridge/timeline.py`.
- Exportación de Evidence Pack y verificación externa — stubs en
  `bridge/export_pack.py` / `bridge/verify_pack.py`.
- Integración con `BufferDB`/`SyncWorker` de `gateway/mqtt/` — pendiente de que se
  decida cuál de las dos colas offline de este repo es la canónica.

# OUT OF SCOPE (siempre, salvo proyecto específico posterior)

- Producción. Datos de clientes o de CTAEX. Credenciales externas.
- Escritura en cualquier SaaS de cultivo o QMS real.
- Automatización de riego, clima o cualquier proceso físico.
- Decisiones de calidad (liberación de lote, cierre de desviación real).
- Validación GxP/GMP, certificación o aprobación regulatoria de cualquier tipo.
- Cualquier afirmación de "inmutabilidad" absoluta — solo hash + procedencia
  verificables, con sus límites documentados.
