"""Entidades de inventario.

El activo es append-only en todos sus campos. `initial_status` es el estado con el que
nació; el vigente se consulta en la vista `asset_current` y se cambia registrando un
evento en `asset_status_event`.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from castuo.common.origen import Origen


@dataclass(frozen=True)
class Asset:
    asset_id: uuid.UUID
    asset_type: str
    geometry: str | None
    owner_ref: uuid.UUID | None      # referencia seudonimizada, nunca una identidad
    initial_status: str
    source_event_id: str
    captured_at: datetime
    schema_version: int
    origen: Origen
