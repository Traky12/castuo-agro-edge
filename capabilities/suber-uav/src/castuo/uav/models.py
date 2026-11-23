"""Entidades de la capa de captura.

`Payload` materializa la escalera de carga útil (ADR-036). Es un conjunto cerrado a
propósito: subir un peldaño es una decisión que se registra en cada misión, no un ajuste
de configuración que nadie recuerda haber hecho.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from castuo.common.origen import Origen


class Payload(str, Enum):
    P0_RGB = "P0_rgb"
    P1_RGB_RTK = "P1_rgb_rtk"
    P2_MULTIESPECTRAL = "P2_multiespectral"
    P3_LIDAR = "P3_lidar"


#: Orden de la escalera. Un peldaño no se salta: cada uno debe haber producido
#: descriptores utilizables antes de justificar el gasto del siguiente.
ESCALERA: tuple[Payload, ...] = (
    Payload.P0_RGB,
    Payload.P1_RGB_RTK,
    Payload.P2_MULTIESPECTRAL,
    Payload.P3_LIDAR,
)


def peldano(payload: Payload) -> int:
    return ESCALERA.index(payload)


@dataclass(frozen=True)
class Mission:
    mission_id: uuid.UUID
    forest_ref: str
    aircraft: str
    payload: Payload
    planned_agl_m: Decimal | None
    overlap_pct: Decimal | None
    authorization_ref: str | None
    operator: uuid.UUID
    extractor_version: str
    source_event_id: str
    flown_at: datetime
    schema_version: int
    origen: Origen


@dataclass(frozen=True)
class Observation:
    observation_id: uuid.UUID
    mission_id: uuid.UUID
    asset_id: uuid.UUID | None
    unit_ref: str
    descriptors: dict
    geometry: str | None
    quality: Decimal
    extractor_version: str
    observed_at: datetime
    schema_version: int
    origen: Origen
