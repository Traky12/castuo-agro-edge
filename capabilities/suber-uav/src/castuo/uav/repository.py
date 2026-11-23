"""Persistencia de misiones y observaciones.

Dos reglas que el motor sostiene y que aquí solo se acompañan:

- La ingesta de misión es idempotente por `source_event_id`, igual que la del activo.
- Una misión con `origen = real` exige referencia de autorización de vuelo. No es una
  comprobación de aplicación: es un CHECK del esquema, porque un vuelo real registrado sin
  autorización sería una evidencia que no se puede enseñar a nadie.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.uav.models import Mission, Observation, Payload


class MissionRepository:
    def __init__(self, conn):
        self.conn = conn

    def ingest_mission(
        self,
        *,
        source_event_id: str,
        forest_ref: str,
        aircraft: str,
        payload: Payload,
        operator: uuid.UUID,
        extractor_version: str,
        flown_at: datetime | None = None,
        planned_agl_m: Decimal | None = None,
        overlap_pct: Decimal | None = None,
        authorization_ref: str | None = None,
        origen: Origen = Origen.SIMULADO,
    ) -> tuple[Mission, bool]:
        """Devuelve (misión, creada). `creada` es False si el evento ya se había ingerido."""
        flown_at = flown_at or datetime.now(timezone.utc)
        row = self.conn.execute(
            """INSERT INTO uav_mission (mission_id, forest_ref, aircraft, payload,
                                        planned_agl_m, overlap_pct, authorization_ref,
                                        operator, extractor_version, source_event_id,
                                        flown_at, schema_version, origen)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (source_event_id) DO NOTHING
               RETURNING mission_id""",
            (uuid.uuid4(), forest_ref, aircraft, payload.value, planned_agl_m, overlap_pct,
             authorization_ref, operator, extractor_version, source_event_id, flown_at,
             SCHEMA_VERSION, origen.value),
        ).fetchone()
        if row is None:
            return self.by_source_event(source_event_id), False
        return self.by_id(row[0]), True

    def _fila(self, fila) -> Mission:
        return Mission(
            mission_id=fila[0], forest_ref=fila[1], aircraft=fila[2],
            payload=Payload(fila[3]), planned_agl_m=fila[4], overlap_pct=fila[5],
            authorization_ref=fila[6], operator=fila[7], extractor_version=fila[8],
            source_event_id=fila[9], flown_at=fila[10], schema_version=fila[11],
            origen=Origen(fila[12]),
        )

    _COLUMNAS = ("mission_id, forest_ref, aircraft, payload, planned_agl_m, overlap_pct, "
                 "authorization_ref, operator, extractor_version, source_event_id, "
                 "flown_at, schema_version, origen")

    def by_id(self, mission_id: uuid.UUID) -> Mission:
        fila = self.conn.execute(
            f"SELECT {self._COLUMNAS} FROM uav_mission WHERE mission_id = %s",
            (mission_id,),
        ).fetchone()
        if fila is None:
            raise LookupError(f"misión inexistente: {mission_id}")
        return self._fila(fila)

    def by_source_event(self, source_event_id: str) -> Mission:
        fila = self.conn.execute(
            f"SELECT {self._COLUMNAS} FROM uav_mission WHERE source_event_id = %s",
            (source_event_id,),
        ).fetchone()
        if fila is None:
            raise LookupError(f"evento de misión inexistente: {source_event_id}")
        return self._fila(fila)


class ObservationRepository:
    def __init__(self, conn):
        self.conn = conn

    def record(
        self,
        *,
        mission_id: uuid.UUID,
        unit_ref: str,
        descriptors: dict,
        quality: Decimal,
        extractor_version: str,
        asset_id: uuid.UUID | None = None,
        geometry: str | None = None,
        observed_at: datetime | None = None,
        origen: Origen = Origen.SIMULADO,
    ) -> tuple[Observation, bool]:
        """Devuelve (observación, creada). Reenviar la misma unidad de la misma misión
        no crea una segunda fila: `UNIQUE (mission_id, unit_ref)` lo impide en el motor."""
        observed_at = observed_at or datetime.now(timezone.utc)
        row = self.conn.execute(
            """INSERT INTO uav_observation (observation_id, mission_id, asset_id, unit_ref,
                                            descriptors, geometry, quality,
                                            extractor_version, observed_at,
                                            schema_version, origen)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (mission_id, unit_ref) DO NOTHING
               RETURNING observation_id""",
            (uuid.uuid4(), mission_id, asset_id, unit_ref, json.dumps(descriptors),
             geometry, quality, extractor_version, observed_at, SCHEMA_VERSION,
             origen.value),
        ).fetchone()
        if row is None:
            return self.by_unit(mission_id, unit_ref), False
        return self.by_id(row[0]), True

    _COLUMNAS = ("observation_id, mission_id, asset_id, unit_ref, descriptors, geometry, "
                 "quality, extractor_version, observed_at, schema_version, origen")

    def _fila(self, fila) -> Observation:
        return Observation(
            observation_id=fila[0], mission_id=fila[1], asset_id=fila[2], unit_ref=fila[3],
            descriptors=fila[4], geometry=fila[5], quality=fila[6],
            extractor_version=fila[7], observed_at=fila[8], schema_version=fila[9],
            origen=Origen(fila[10]),
        )

    def by_id(self, observation_id: uuid.UUID) -> Observation:
        fila = self.conn.execute(
            f"SELECT {self._COLUMNAS} FROM uav_observation WHERE observation_id = %s",
            (observation_id,),
        ).fetchone()
        if fila is None:
            raise LookupError(f"observación inexistente: {observation_id}")
        return self._fila(fila)

    def by_unit(self, mission_id: uuid.UUID, unit_ref: str) -> Observation:
        fila = self.conn.execute(
            f"SELECT {self._COLUMNAS} FROM uav_observation "
            "WHERE mission_id = %s AND unit_ref = %s",
            (mission_id, unit_ref),
        ).fetchone()
        if fila is None:
            raise LookupError(f"observación inexistente: {mission_id}/{unit_ref}")
        return self._fila(fila)

    def by_mission(self, mission_id: uuid.UUID) -> list[Observation]:
        filas = self.conn.execute(
            f"SELECT {self._COLUMNAS} FROM uav_observation "
            "WHERE mission_id = %s ORDER BY unit_ref",
            (mission_id,),
        ).fetchall()
        return [self._fila(f) for f in filas]
