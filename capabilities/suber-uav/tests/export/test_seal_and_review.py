"""Sello local, aceptación experta y anclaje certificado posterior."""
from __future__ import annotations

import json
import pathlib
import uuid

import psycopg
import pytest

from castuo.detection import service
from castuo.detection.repository import DetectionRepository
from castuo.export.seal import SealRepository, detection_canonical_payload
from castuo.review.models import ACCEPTED_BY_EXPERT, ReviewRepository

pytestmark = pytest.mark.integration
FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures/synthetic/vuelo_sintetico.json"


@pytest.fixture
def detection(owner_conn):
    evidence = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return DetectionRepository(owner_conn).add(
        service.infer(evidence), evidence_id=evidence["evidence_id"])


def test_expert_acceptance_without_seal_is_rejected(owner_conn, detection):
    """Criterio 8. La aceptación experta sin sello no llega a existir.

    Dos capas la impiden: el trigger `review_seal_guard` (que salta primero, con un
    mensaje que distingue «sin sello» de «sello inexistente») y el CHECK
    `review_expert_requires_seal`. La prueba acepta cualquiera de las dos.
    """
    with pytest.raises((psycopg.errors.RestrictViolation, psycopg.errors.CheckViolation),
                       match="CASTUO_SEAL|review_expert_requires_seal"):
        ReviewRepository(owner_conn).add(
            detection_id=detection.detection_id, verdict=ACCEPTED_BY_EXPERT,
            review_type="expert", actor=uuid.uuid4(), seal_id=None)
    owner_conn.rollback()


def test_preliminary_review_does_not_require_a_seal(owner_conn, detection):
    """Ajuste pedido: el sello es obligatorio solo para la aceptación experta.
    Un rechazo técnico o una revisión preliminar tienen que poder registrarse."""
    reviews = ReviewRepository(owner_conn)
    reviews.add(detection_id=detection.detection_id, verdict="preliminary",
                review_type="preliminary", actor=uuid.uuid4())
    reviews.add(detection_id=detection.detection_id, verdict="technical_reject",
                review_type="technical", actor=uuid.uuid4())
    assert len(reviews.for_detection(detection.detection_id)) == 2


def test_seal_from_another_detection_is_rejected(owner_conn, detection):
    """Un CHECK solo puede ver que seal_id no es nulo; que el sello sea EL de esta
    detección lo comprueba el trigger."""
    evidence = json.loads(FIXTURE.read_text(encoding="utf-8"))
    otra = DetectionRepository(owner_conn).add(
        service.infer(evidence, model_version="0.9.0"), evidence_id="ev-otra")
    seal_ajeno = SealRepository(owner_conn).seal_detection(otra)

    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_SEAL"):
        ReviewRepository(owner_conn).add(
            detection_id=detection.detection_id, verdict=ACCEPTED_BY_EXPERT,
            review_type="expert", actor=uuid.uuid4(), seal_id=seal_ajeno)
    owner_conn.rollback()


def test_expert_acceptance_with_a_valid_seal_is_accepted(owner_conn, detection):
    seals = SealRepository(owner_conn)
    seal_id = seals.seal_detection(detection)
    review = ReviewRepository(owner_conn).add(
        detection_id=detection.detection_id, verdict=ACCEPTED_BY_EXPERT,
        review_type="expert", actor=uuid.uuid4(), seal_id=seal_id)
    assert review.seal_id == seal_id


def test_adding_the_rfc3161_token_does_not_change_the_sealed_content(owner_conn, detection):
    """Criterio 9. El token se ancla en su propia tabla: el sello base no se toca, así que
    un paquete exportado antes del anclaje sigue verificando después."""
    seals = SealRepository(owner_conn)
    seal_id = seals.seal_detection(detection)
    antes = seals.get(seal_id)

    from castuo.export.anchor import synthetic_token
    seals.anchor(seal_id, synthetic_token(antes["canonical_hash"]), "autoridad-de-pruebas")
    despues = seals.get(seal_id)

    assert antes["canonical_hash"] == despues["canonical_hash"]
    assert antes["sealed_at"] == despues["sealed_at"]
    assert len(seals.anchors_for(seal_id)) == 1


def test_the_seal_covers_the_canonical_content_of_the_detection(owner_conn, detection):
    from castuo.common.hashing import hash_payload
    seals = SealRepository(owner_conn)
    seal_id = seals.seal_detection(detection)
    assert seals.get(seal_id)["canonical_hash"] == hash_payload(
        detection_canonical_payload(detection))
