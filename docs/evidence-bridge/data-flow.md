# Evidence Bridge (EB-POC-001) — flujo de datos (estado actual)

```
fixtures/*.jsonl (datos sintéticos, solo lectura)
        |
        v
bridge/ingest.py -------- lee línea a línea, JSON parseable?
        |
        v
bridge/validate.py ------ valida contra JSON Schema (4 tipos)
        |                 (rechaza sin inventar campos ausentes)
        v
bridge/provenance.py ---- hash canónico sha256, encadenado con
        |                 previous_event_hash
        v
offline/queue_adapter.py  persiste en tabla propia (evidence_bridge_events),
        |                 idempotente por event_id — sobrevive caída de red
        v
   [ITERACIÓN 2 — stubs por ahora]
   bridge/reconcile.py    duplicados / huecos / retrasos
   bridge/timeline.py     evento -> alerta -> observación -> acción -> QMS -> cierre
   bridge/export_pack.py  manifest.json + timeline exportado
   bridge/verify_pack.py  verificación independiente de hashes
```

No hay ninguna flecha de escritura hacia un SaaS de cultivo o QMS real — todo el
flujo es de solo lectura sobre datos sintéticos, terminando en almacenamiento local.
