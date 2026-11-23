"""Anclaje RFC 3161: los cuatro estados del contrato.

Quien lea el resultado tiene que saber qué tiene delante: un sello local sin anclaje no es
lo mismo que un anclaje que certifica otro hash, y ninguno de los dos es un token ilegible.
"""
from __future__ import annotations

import hashlib
import uuid

import pytest

from castuo.export.anchor import (
    EstadoAnclaje, extract_message_imprint, synthetic_token, verify_anchor,
)

HASH = hashlib.sha256(b"contenido canonico").digest()


def test_a_synthetic_token_is_real_der_and_carries_the_imprint():
    token = synthetic_token(HASH)
    assert token[0] == 0x30                      # SEQUENCE
    assert extract_message_imprint(token) == HASH


def test_anchor_matching_the_sealed_hash_is_valid():
    assert verify_anchor(HASH, synthetic_token(HASH)) is EstadoAnclaje.ANCLAJE_VALIDO


def test_anchor_of_another_hash_is_detected():
    """Un token válido de otra cosa no certifica esta evidencia."""
    otro = hashlib.sha256(b"otro contenido").digest()
    assert verify_anchor(HASH, synthetic_token(otro)) is EstadoAnclaje.ANCLAJE_DE_OTRO_HASH


def test_absence_of_anchor_is_its_own_state():
    """No es un error: es un sello local sin certificar, y hay que poder decirlo así."""
    assert verify_anchor(HASH, None) is EstadoAnclaje.SELLO_LOCAL_SIN_ANCLAJE


@pytest.mark.parametrize("basura", [b"", b"no soy DER", b"\x30\x03\x02\x01\x00"])
def test_unreadable_token_is_not_confused_with_a_wrong_hash(basura):
    assert verify_anchor(HASH, basura) is EstadoAnclaje.TOKEN_ILEGIBLE


@pytest.mark.integration
def test_anchoring_does_not_change_the_seal(owner_conn):
    """El anclaje añade información sobre el sello; no lo reescribe."""
    import json, pathlib
    from castuo.detection import service
    from castuo.detection.repository import DetectionRepository
    from castuo.export.seal import SealRepository

    fixture = pathlib.Path(__file__).resolve().parents[1] / "fixtures/synthetic/vuelo_sintetico.json"
    evidencia = json.loads(fixture.read_text(encoding="utf-8"))
    deteccion = DetectionRepository(owner_conn).add(
        service.infer(evidencia), evidence_id=evidencia["evidence_id"])

    sellos = SealRepository(owner_conn)
    seal_id = sellos.seal_detection(deteccion)
    antes = sellos.get(seal_id)
    assert sellos.verify_anchors(seal_id) == [EstadoAnclaje.SELLO_LOCAL_SIN_ANCLAJE]

    sellos.anchor(seal_id, synthetic_token(antes["canonical_hash"]), "autoridad-de-pruebas")
    assert sellos.get(seal_id) == antes
    assert sellos.verify_anchors(seal_id) == [EstadoAnclaje.ANCLAJE_VALIDO]


@pytest.mark.integration
def test_an_anchor_for_the_wrong_hash_is_caught(owner_conn):
    import json, pathlib
    from castuo.detection import service
    from castuo.detection.repository import DetectionRepository
    from castuo.export.seal import SealRepository

    fixture = pathlib.Path(__file__).resolve().parents[1] / "fixtures/synthetic/vuelo_sintetico.json"
    evidencia = json.loads(fixture.read_text(encoding="utf-8"))
    deteccion = DetectionRepository(owner_conn).add(
        service.infer(evidencia), evidence_id=evidencia["evidence_id"])
    sellos = SealRepository(owner_conn)
    seal_id = sellos.seal_detection(deteccion)

    sellos.anchor(seal_id, synthetic_token(hashlib.sha256(b"otra cosa").digest()), "tsa-x")
    assert sellos.verify_anchors(seal_id) == [EstadoAnclaje.ANCLAJE_DE_OTRO_HASH]
