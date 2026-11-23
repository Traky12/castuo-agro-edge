"""Estado del activo como secuencia de eventos.

El estado no es una columna que se reescribe: es la proyección del último evento. Así queda
registrado quién lo cambió, cuándo y por qué, y el rol de aplicación no necesita UPDATE en
ninguna tabla.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from castuo.common.origen import SCHEMA_VERSION, Origen

#: Transiciones declaradas. El motor las impone; esta tabla las documenta y permite
#: comprobarlas sin ir a la base de datos.
TRANSICIONES = {
    ("detectado", "validado"),
    ("detectado", "descartado"),
    ("validado", "descartado"),
    ("pendiente", "detectado"),
    ("pendiente", "descartado"),
}


@dataclass(frozen=True)
class AssetStatusEvent:
    status_event_id: uuid.UUID
    asset_id: uuid.UUID
    sequence_no: int
    from_status: str | None
    to_status: str
    actor: uuid.UUID
    reason: str | None
    occurred_at: datetime
    schema_version: int
    origen: Origen


class AssetStatusRepository:
    def __init__(self, conn):
        self.conn = conn

    def current(self, asset_id: uuid.UUID) -> str:
        return self.conn.execute(
            "SELECT status FROM asset_current WHERE asset_id = %s", (asset_id,)
        ).fetchone()[0]

    def transition(self, *, asset_id: uuid.UUID, to_status: str, actor: uuid.UUID,
                   reason: str | None = None,
                   origen: Origen = Origen.SIMULADO) -> AssetStatusEvent:
        """Registra una transición desde el estado vigente. El motor rechaza los saltos
        no declarados y los que parten de un estado que ya no es el actual."""
        with self.conn.transaction():
            # Mismo bloqueo que usa el trigger: sin él, dos transiciones simultáneas
            # calcularían el mismo número de secuencia.
            self.conn.execute(
                "SELECT pg_advisory_xact_lock(hashtext('asset_status'), hashtext(%s))",
                (str(asset_id),))
            from_status = self.current(asset_id)
            ultima = self.conn.execute(
                "SELECT max(sequence_no) FROM asset_status_event WHERE asset_id = %s",
                (asset_id,)).fetchone()[0]
            sequence_no = (ultima or 0) + 1
            status_event_id = uuid.uuid4()
            row = self.conn.execute(
                """INSERT INTO asset_status_event (status_event_id, asset_id, sequence_no,
                            from_status, to_status, actor, reason, schema_version, origen)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING occurred_at""",
                (status_event_id, asset_id, sequence_no, from_status, to_status, actor,
                 reason, SCHEMA_VERSION, origen.value),
            ).fetchone()
        return AssetStatusEvent(status_event_id, asset_id, sequence_no, from_status,
                                to_status, actor, reason, row[0], SCHEMA_VERSION, origen)

    def history(self, asset_id: uuid.UUID) -> list[AssetStatusEvent]:
        rows = self.conn.execute(
            """SELECT status_event_id, asset_id, sequence_no, from_status, to_status,
                      actor, reason, occurred_at, schema_version, origen
               FROM asset_status_event WHERE asset_id = %s
               ORDER BY sequence_no""", (asset_id,)
        ).fetchall()
        return [AssetStatusEvent(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
                                 Origen(r[9]))
                for r in rows]
