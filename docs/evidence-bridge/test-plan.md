# Evidence Bridge (EB-POC-001) — plan de pruebas

| Fixture / caso | Resultado esperado | Test |
|---|---|---|
| `fixtures/normal.jsonl` | Todos los eventos validan y producen `payload_hash` | `test_ingest.py`, `test_provenance.py` |
| `fixtures/deviation_environmental.jsonl` | Valida igual que un evento normal — la clasificación de "desviación" es responsabilidad de `timeline.py` (iteración 2), no de la validación | `test_ingest.py` |
| `fixtures/duplicate.jsonl` | Ambas líneas validan individualmente (la detección de duplicado es de `reconcile.py`, iteración 2) | `test_ingest.py` |
| `fixtures/delayed.jsonl` | Valida; `occurred_at` y `received_at` se conservan sin fusionar | `test_ingest.py` |
| `fixtures/corrupt_malformed.jsonl` | Línea sin `unit`/`schema_version` → `valid=False`; línea con `occurred_at` no-fecha → `valid=False`; línea no-JSON → `valid=False` con error de parseo | `test_ingest.py`, `test_validate.py` |
| `fixtures/sequence_gap.jsonl` | Todos validan; el hueco en `sequence_number` (1,2,4) no se detecta aquí (`reconcile.py`, iteración 2) | `test_ingest.py` |
| Evento con payload alterado tras el hash | `verify_event_hash` devuelve `False` | `test_provenance.py` |
| Cadena de 2+ eventos | `previous_event_hash` del segundo coincide con `payload_hash` del primero, y ambos verifican | `test_provenance.py` |
| Cola offline: reintento tras "reconexión" | Reencolar el mismo `event_id` no duplica la fila (`INSERT OR IGNORE`) | `test_offline_continuity.py` |
| Cola offline: pendientes → sincronizado | `pending()` deja de listar el evento tras `mark_synced()` | `test_offline_continuity.py` |
