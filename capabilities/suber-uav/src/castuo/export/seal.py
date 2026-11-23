"""Sello local y anclaje certificado.

Dos conceptos separados a propósito. El **sello local** —hash canónico del sujeto más la
hora del servidor— es lo que bloquea la aceptación experta, y existe desde este slice. El
**anclaje certificado** (token RFC 3161 de una autoridad de tiempo) se añade después, en
su propia tabla: así el contenido base sellado no cambia nunca, que es lo que permite que
un paquete exportado hoy siga verificando mañana con el token adjunto.
"""
from __future__ import annotations

import uuid

from castuo.common.hashing import hash_payload
from castuo.common.origen import SCHEMA_VERSION, Origen


def detection_canonical_payload(detection) -> dict:
    """Contenido sellable de una detección: lo determinista y nada más."""
    return {
        "evidence_id": detection.evidence_id,
        "model_id": detection.model_id,
        "model_version": detection.model_version,
        "params": detection.params,
        "label": detection.label,
        "confidence": detection.confidence,
        "geometry": detection.geometry,
        "input_hash": detection.input_hash,
        "result_hash": detection.result_hash,
        "origen": detection.origen.value,
        "schema_version": detection.schema_version,
    }


class SealRepository:
    def __init__(self, conn):
        self.conn = conn

    def seal_detection(self, detection, origen: Origen = Origen.SIMULADO) -> uuid.UUID:
        seal_id = uuid.uuid4()
        canonical_hash = hash_payload(detection_canonical_payload(detection))
        self.conn.execute(
            """INSERT INTO seal (seal_id, subject_type, subject_id, canonical_hash,
                                 seal_kind, schema_version, origen)
               VALUES (%s, 'detection', %s, %s, 'local', %s, %s)""",
            (seal_id, detection.detection_id, canonical_hash, SCHEMA_VERSION, origen.value),
        )
        return seal_id

    def get(self, seal_id: uuid.UUID) -> dict:
        r = self.conn.execute(
            """SELECT seal_id, subject_type, subject_id, canonical_hash, seal_kind,
                      sealed_at, schema_version, origen FROM seal WHERE seal_id = %s""",
            (seal_id,),
        ).fetchone()
        return {"seal_id": r[0], "subject_type": r[1], "subject_id": r[2],
                "canonical_hash": bytes(r[3]), "seal_kind": r[4], "sealed_at": r[5],
                "schema_version": r[6], "origen": r[7]}

    def anchor(self, seal_id: uuid.UUID, tsa_token: bytes, authority: str,
               origen: Origen = Origen.SIMULADO) -> uuid.UUID:
        """Ancla un token RFC 3161 SIN tocar el sello base (criterio 9)."""
        anchor_id = uuid.uuid4()
        self.conn.execute(
            """INSERT INTO seal_anchor (anchor_id, seal_id, tsa_token, authority,
                                        schema_version, origen)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (anchor_id, seal_id, tsa_token, authority, SCHEMA_VERSION, origen.value),
        )
        return anchor_id

    def anchors_for(self, seal_id: uuid.UUID) -> list[dict]:
        """Anclajes del sello. `anchored_at` no viaja en el paquete: es marca de escritura,
        no contenido, y meterla haría variar el hash entre exportaciones."""
        rows = self.conn.execute(
            """SELECT anchor_id, tsa_token, authority, origen FROM seal_anchor
               WHERE seal_id = %s ORDER BY anchored_at, anchor_id""", (seal_id,)
        ).fetchall()
        return [{"anchor_id": str(r[0]), "tsa_token": bytes(r[1]),
                 "authority": r[2], "origen": r[3]} for r in rows]

    def verify_anchors(self, seal_id: uuid.UUID) -> list:
        """Estado de cada anclaje frente al hash que dice certificar."""
        from castuo.export.anchor import verify_anchor
        canonical_hash = self.get(seal_id)["canonical_hash"]
        anclajes = self.anchors_for(seal_id)
        if not anclajes:
            return [verify_anchor(canonical_hash, None)]
        return [verify_anchor(canonical_hash, a["tsa_token"]) for a in anclajes]
