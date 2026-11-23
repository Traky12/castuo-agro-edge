"""Revisión humana: entidad append-only separada de la detección (C-2).

La aceptación experta exige un sello local previo; una revisión preliminar o un rechazo
técnico no, porque bloquearlos impediría registrar el trabajo cotidiano de campo.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from castuo.common.origen import SCHEMA_VERSION, Origen

ACCEPTED_BY_EXPERT = "accepted_by_expert"


@dataclass(frozen=True)
class Review:
    review_id: uuid.UUID
    detection_id: uuid.UUID
    verdict: str
    review_type: str
    actor: uuid.UUID
    reviewed_at: datetime
    seal_id: uuid.UUID | None
    schema_version: int
    origen: Origen


class ReviewRepository:
    def __init__(self, conn):
        self.conn = conn

    def add(self, *, detection_id: uuid.UUID, verdict: str, review_type: str,
            actor: uuid.UUID, seal_id: uuid.UUID | None = None,
            origen: Origen = Origen.SIMULADO) -> Review:
        review_id = uuid.uuid4()
        row = self.conn.execute(
            """INSERT INTO review (review_id, detection_id, verdict, review_type, actor,
                                   seal_id, schema_version, origen)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING reviewed_at""",
            (review_id, detection_id, verdict, review_type, actor, seal_id,
             SCHEMA_VERSION, origen.value),
        ).fetchone()
        return Review(review_id, detection_id, verdict, review_type, actor, row[0],
                      seal_id, SCHEMA_VERSION, origen)

    def for_detection(self, detection_id: uuid.UUID) -> list[Review]:
        rows = self.conn.execute(
            """SELECT review_id, detection_id, verdict, review_type, actor, reviewed_at,
                      seal_id, schema_version, origen
               FROM review WHERE detection_id = %s ORDER BY reviewed_at""",
            (detection_id,),
        ).fetchall()
        return [Review(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], Origen(r[8]))
                for r in rows]
