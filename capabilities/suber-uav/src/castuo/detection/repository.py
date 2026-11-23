"""Persistencia de detecciones y propuestas de activo.

Nada se actualiza: una inferencia nueva es una fila nueva. Dos detecciones sobre la misma
evidencia con distinta versión de modelo conviven, que es exactamente lo que permite
comparar versiones después.
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal

from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.detection.models import Detection


class DetectionRepository:
    def __init__(self, conn):
        self.conn = conn

    def add(self, result: dict, *, evidence_id: str, asset_id: uuid.UUID | None = None) -> Detection:
        detection_id = uuid.uuid4()
        row = self.conn.execute(
            """INSERT INTO detection (detection_id, asset_id, evidence_id, model_id,
                    model_version, label, confidence, geometry, params, input_hash,
                    result_hash, schema_version, origen)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s)
               RETURNING detected_at""",
            (detection_id, asset_id, evidence_id, result["model_id"], result["model_version"],
             result["label"], result["confidence"], result["geometry"],
             json.dumps(result["params"], sort_keys=True), result["input_hash"],
             result["result_hash"], SCHEMA_VERSION, result["origen"].value),
        ).fetchone()
        return Detection(
            detection_id, asset_id, evidence_id, result["model_id"], result["model_version"],
            result["label"], Decimal(result["confidence"]), result["geometry"], result["params"],
            result["input_hash"], result["result_hash"], row[0], SCHEMA_VERSION, result["origen"],
        )

    def get(self, detection_id: uuid.UUID) -> Detection:
        r = self.conn.execute(
            """SELECT detection_id, asset_id, evidence_id, model_id, model_version, label,
                      confidence, geometry, params, input_hash, result_hash, detected_at,
                      schema_version, origen
               FROM detection WHERE detection_id = %s""",
            (detection_id,),
        ).fetchone()
        return Detection(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
                         bytes(r[9]), bytes(r[10]), r[11], r[12], Origen(r[13]))

    def propose_asset(self, detection_id: uuid.UUID, asset_id: uuid.UUID,
                      origen: Origen = Origen.SIMULADO) -> tuple[uuid.UUID, bool]:
        """Vincula una detección con el activo que propone, sin tocar la detección.

        Repetir la misma propuesta es idempotente: la unicidad de (detection_id, asset_id)
        vive en el esquema, así que reenviar el mismo mensaje no duplica el vínculo ni
        obliga al llamante a comprobar antes.
        Devuelve (proposal_id, creada).
        """
        proposal_id = uuid.uuid4()
        row = self.conn.execute(
            """INSERT INTO asset_proposal (proposal_id, detection_id, asset_id,
                                           schema_version, origen)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (detection_id, asset_id) DO NOTHING
               RETURNING proposal_id""",
            (proposal_id, detection_id, asset_id, SCHEMA_VERSION, origen.value),
        ).fetchone()
        if row is not None:
            return row[0], True
        existente = self.conn.execute(
            """SELECT proposal_id FROM asset_proposal
               WHERE detection_id = %s AND asset_id = %s""",
            (detection_id, asset_id),
        ).fetchone()
        return existente[0], False

    def assets_for(self, detection_id: uuid.UUID) -> list[uuid.UUID]:
        rows = self.conn.execute(
            "SELECT asset_id FROM asset_proposal WHERE detection_id = %s ORDER BY proposed_at",
            (detection_id,),
        ).fetchall()
        return [r[0] for r in rows]
