"""Persistencia de inventario, con ingesta idempotente.

`source_event_id` es UNIQUE en el esquema: reenviar el mismo evento de ingesta no crea
un segundo activo. La idempotencia se apoya en el motor y no en una comprobación previa
en Python, que dos procesos simultáneos se saltarían.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.inventory.models import Asset


class InventoryRepository:
    def __init__(self, conn):
        self.conn = conn

    def ingest_asset(
        self,
        *,
        source_event_id: str,
        asset_type: str,
        geometry: str | None,
        captured_at: datetime | None = None,
        owner_ref: uuid.UUID | None = None,
        origen: Origen = Origen.SIMULADO,
        initial_status: str = "detectado",
    ) -> tuple[Asset, bool]:
        """Devuelve (activo, creado). `creado` es False si el evento ya se había ingerido."""
        captured_at = captured_at or datetime.now(timezone.utc)
        row = self.conn.execute(
            """INSERT INTO asset (asset_id, asset_type, geometry, owner_ref, initial_status,
                                  source_event_id, captured_at, schema_version, origen)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (source_event_id) DO NOTHING
               RETURNING asset_id""",
            (uuid.uuid4(), asset_type, geometry, owner_ref, initial_status,
             source_event_id, captured_at, SCHEMA_VERSION, origen.value),
        ).fetchone()

        if row is not None:
            return self.get_by_source_event(source_event_id), True
        return self.get_by_source_event(source_event_id), False

    def get_by_source_event(self, source_event_id: str) -> Asset:
        r = self.conn.execute(
            """SELECT asset_id, asset_type, geometry, owner_ref, initial_status,
                      source_event_id, captured_at, schema_version, origen
               FROM asset WHERE source_event_id = %s""",
            (source_event_id,),
        ).fetchone()
        return Asset(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], Origen(r[8]))

    def get(self, asset_id: uuid.UUID) -> Asset:
        r = self.conn.execute(
            """SELECT asset_id, asset_type, geometry, owner_ref, initial_status,
                      source_event_id, captured_at, schema_version, origen
               FROM asset WHERE asset_id = %s""",
            (asset_id,),
        ).fetchone()
        return Asset(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], Origen(r[8]))

    def current_status(self, asset_id: uuid.UUID) -> str:
        """Estado vigente, proyectado desde los eventos. No hay columna que actualizar."""
        return self.conn.execute(
            "SELECT status FROM asset_current WHERE asset_id = %s", (asset_id,)
        ).fetchone()[0]
