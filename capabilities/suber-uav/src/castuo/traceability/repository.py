"""Persistencia de la cadena de trazabilidad.

El `sequence_no` y el `previous_trace_hash` se calculan dentro de un bloqueo por
dispositivo: sin él, dos escrituras simultáneas del mismo dispositivo calcularían el
mismo número y la unicidad `(device_id, sequence_no)` haría fallar una de las dos.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from castuo.common.hashing import hash_payload, trace_event_hash
from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.storage.transactions import device_chain_lock
from castuo.traceability.events import TraceEvent


class TraceRepository:
    def __init__(self, conn):
        self.conn = conn

    def append(self, *, device_id: uuid.UUID, entity_type: str, entity_id: uuid.UUID,
               event_type: str, actor: uuid.UUID, payload: dict,
               origen: Origen = Origen.SIMULADO) -> TraceEvent:
        payload_hash = hash_payload(payload)
        with device_chain_lock(self.conn, device_id):
            last = self.conn.execute(
                """SELECT sequence_no, event_hash FROM trace_event
                   WHERE device_id = %s ORDER BY sequence_no DESC LIMIT 1""",
                (device_id,),
            ).fetchone()
            sequence_no = 1 if last is None else last[0] + 1
            previous = None if last is None else bytes(last[1])

            # La hora forma parte del contenido hasheado, así que se fija aquí y se
            # inserta explícitamente: dejar que la calcule el DEFAULT daría un event_hash
            # que no corresponde a la fila guardada.
            occurred_at = datetime.now(timezone.utc)
            event_hash = trace_event_hash(
                device_id=device_id, sequence_no=sequence_no, entity_type=entity_type,
                entity_id=entity_id, event_type=event_type, actor=actor,
                occurred_at=occurred_at, payload_hash=payload_hash,
                previous_trace_hash=previous, schema_version=SCHEMA_VERSION,
                origen=origen.value,
            )

            trace_id = uuid.uuid4()
            self.conn.execute(
                """INSERT INTO trace_event (trace_id, device_id, entity_type, entity_id,
                        event_type, actor, sequence_no, occurred_at, payload_hash,
                        event_hash, previous_trace_hash, schema_version, origen)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (trace_id, device_id, entity_type, entity_id, event_type, actor,
                 sequence_no, occurred_at, payload_hash, event_hash, previous,
                 SCHEMA_VERSION, origen.value),
            )

        return TraceEvent(trace_id, device_id, entity_type, entity_id, event_type, actor,
                          sequence_no, occurred_at, payload_hash, event_hash, previous,
                          SCHEMA_VERSION, origen)

    def for_device(self, device_id: uuid.UUID) -> list[TraceEvent]:
        rows = self.conn.execute(
            """SELECT trace_id, device_id, entity_type, entity_id, event_type, actor,
                      sequence_no, occurred_at, payload_hash, event_hash,
                      previous_trace_hash, schema_version, origen
               FROM trace_event WHERE device_id = %s ORDER BY sequence_no""",
            (device_id,),
        ).fetchall()
        return [TraceEvent(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], bytes(r[8]),
                           bytes(r[9]), bytes(r[10]) if r[10] is not None else None,
                           r[11], Origen(r[12]))
                for r in rows]

    def for_entity(self, entity_type: str, entity_id: uuid.UUID) -> list[TraceEvent]:
        rows = self.conn.execute(
            """SELECT trace_id, device_id, entity_type, entity_id, event_type, actor,
                      sequence_no, occurred_at, payload_hash, event_hash,
                      previous_trace_hash, schema_version, origen
               FROM trace_event WHERE entity_type = %s AND entity_id = %s
               ORDER BY occurred_at""",
            (entity_type, entity_id),
        ).fetchall()
        return [TraceEvent(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], bytes(r[8]),
                           bytes(r[9]), bytes(r[10]) if r[10] is not None else None,
                           r[11], Origen(r[12]))
                for r in rows]
