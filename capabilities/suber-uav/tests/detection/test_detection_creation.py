"""Detección: creación, propuesta de activo y rechazo de inferencias sin versión."""
from __future__ import annotations

import json
import pathlib

import pytest

from castuo.common.origen import Origen
from castuo.detection import service
from castuo.detection.repository import DetectionRepository
from castuo.inventory.repository import InventoryRepository

pytestmark = pytest.mark.integration

FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures/synthetic/vuelo_sintetico.json"


@pytest.fixture
def evidence():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_detection_records_model_and_hashes(owner_conn, evidence):
    result = service.infer(evidence)
    detection = DetectionRepository(owner_conn).add(result, evidence_id=evidence["evidence_id"])
    assert detection.model_id == service.MODEL_ID
    assert detection.model_version == service.MODEL_VERSION
    assert len(detection.input_hash) == 32 and len(detection.result_hash) == 32


def test_detection_without_model_version_is_rejected(owner_conn, evidence):
    """Criterio 3, en dos capas: la de servicio y la del esquema."""
    with pytest.raises(service.MissingModelVersion):
        service.infer(evidence, model_version="")

    import psycopg
    result = service.infer(evidence)
    result["model_version"] = "   "
    with pytest.raises(psycopg.errors.CheckViolation):
        DetectionRepository(owner_conn).add(result, evidence_id=evidence["evidence_id"])
    owner_conn.rollback()


def test_detection_can_propose_an_asset_without_being_modified(owner_conn, evidence):
    """C-1. La detección nace sin activo y lo propone después; el vínculo va en su propia
    tabla porque la detección no se puede reescribir."""
    detections = DetectionRepository(owner_conn)
    detection = detections.add(service.infer(evidence), evidence_id=evidence["evidence_id"])
    assert detection.asset_id is None

    asset, _ = InventoryRepository(owner_conn).ingest_asset(
        source_event_id=f"prop-{detection.detection_id}", asset_type="arbol",
        geometry=evidence["geometry"])
    detections.propose_asset(detection.detection_id, asset.asset_id)

    assert detections.assets_for(detection.detection_id) == [asset.asset_id]
    assert detections.get(detection.detection_id).asset_id is None  # intacta


def test_new_detection_does_not_modify_the_previous_one(owner_conn, evidence):
    """Criterio 2. Dos inferencias sobre la misma evidencia conviven."""
    repo = DetectionRepository(owner_conn)
    first = repo.add(service.infer(evidence), evidence_id=evidence["evidence_id"])
    second = repo.add(service.infer(evidence, model_version="0.2.0"),
                      evidence_id=evidence["evidence_id"])

    reloaded = repo.get(first.detection_id)
    assert reloaded.model_version == "0.1.0"
    assert reloaded.result_hash == first.result_hash
    assert second.detection_id != first.detection_id
    assert owner_conn.execute("SELECT count(*) FROM detection").fetchone()[0] == 2
