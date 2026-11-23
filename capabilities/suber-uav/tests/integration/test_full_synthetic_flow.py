"""Flujo sintético completo, de la evidencia al paquete verificable.

Es la prueba que demuestra el valor del slice: que una observación se convierte en una
evidencia auditable y reproducible. Todo con `origen = simulado`, marcado desde el esquema.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import uuid

import pytest

from castuo.common.origen import Origen
from castuo.detection import service
from castuo.detection.repository import DetectionRepository
from castuo.export.package import build_package, package_content
from castuo.export.seal import SealRepository
from castuo.inventory.repository import InventoryRepository
from castuo.inventory.status import AssetStatusRepository
from castuo.export.anchor import EstadoAnclaje, synthetic_token
from castuo.review.models import ACCEPTED_BY_EXPERT, ReviewRepository
from castuo.traceability import events as ev
from castuo.traceability.chain import verify_chain
from castuo.traceability.repository import TraceRepository

pytestmark = pytest.mark.integration

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/synthetic"
VERIFIER = ROOT / "scripts/verify_package.py"


def _run_flow(conn, device_id, evidence):
    """Recorre el sistema entero una sola vez y devuelve el paquete exportado."""
    inventory = InventoryRepository(conn)
    estados = AssetStatusRepository(conn)
    detections = DetectionRepository(conn)
    seals = SealRepository(conn)
    reviews = ReviewRepository(conn)
    trace = TraceRepository(conn)
    actor = uuid.uuid4()

    # 1. Ingesta idempotente de la evidencia: el mismo evento dos veces, un solo activo.
    asset, created_1 = inventory.ingest_asset(
        source_event_id=evidence["evidence_id"], asset_type="parcela",
        geometry=evidence["geometry"], origen=Origen.SIMULADO)
    _, created_2 = inventory.ingest_asset(
        source_event_id=evidence["evidence_id"], asset_type="parcela",
        geometry=evidence["geometry"], origen=Origen.SIMULADO)
    assert (created_1, created_2) == (True, False)
    trace.append(device_id=device_id, entity_type="asset", entity_id=asset.asset_id,
                 event_type=ev.ASSET_INGESTED, actor=actor,
                 payload={"source_event_id": evidence["evidence_id"]})

    # 2. Detección determinista sobre la evidencia.
    detection = detections.add(service.infer(evidence), evidence_id=evidence["evidence_id"])
    trace.append(device_id=device_id, entity_type="detection", entity_id=detection.detection_id,
                 event_type=ev.DETECTION_CREATED, actor=actor,
                 payload={"result_hash": detection.result_hash.hex()})

    # 3. La detección propone el activo, sin modificarse.
    detections.propose_asset(detection.detection_id, asset.asset_id)
    estados.transition(asset_id=asset.asset_id, to_status="validado", actor=actor,
                       reason="propuesto por la deteccion")
    trace.append(device_id=device_id, entity_type="asset", entity_id=asset.asset_id,
                 event_type=ev.ASSET_PROPOSED, actor=actor,
                 payload={"detection_id": str(detection.detection_id)})

    # 4. Sello local. Solo después de esto puede entrar la aceptación experta.
    seal_id = seals.seal_detection(detection)
    trace.append(device_id=device_id, entity_type="seal", entity_id=seal_id,
                 event_type=ev.SEAL_CREATED, actor=actor, payload={"seal_id": str(seal_id)})

    review = reviews.add(detection_id=detection.detection_id, verdict=ACCEPTED_BY_EXPERT,
                         review_type="expert", actor=actor, seal_id=seal_id)
    trace.append(device_id=device_id, entity_type="review", entity_id=review.review_id,
                 event_type=ev.REVIEW_RECORDED, actor=actor, payload={"verdict": review.verdict})

    # 5. Paquete exportable.
    package = build_package(
        detection=detections.get(detection.detection_id),
        asset=inventory.get(asset.asset_id),
        asset_status=estados.current(asset.asset_id),
        status_history=estados.history(asset.asset_id),
        proposals=[(detection.detection_id, a, "simulado")
                   for a in detections.assets_for(detection.detection_id)],
        reviews=reviews.for_detection(detection.detection_id),
        seal=seals.get(seal_id),
        anchors=seals.anchors_for(seal_id),
        trace_events=trace.for_device(device_id),
    )
    trace.append(device_id=device_id, entity_type="package", entity_id=detection.detection_id,
                 event_type=ev.PACKAGE_EXPORTED, actor=actor,
                 payload={"package_hash": package["package_hash"]})
    verify_chain(trace.for_device(device_id))
    return package, detection, asset, seal_id, seals


@pytest.fixture
def evidence():
    return json.loads((FIXTURES / "vuelo_sintetico.json").read_text(encoding="utf-8"))


def test_full_flow_produces_a_package_that_reconstructs_the_origin(owner_conn, device_id, evidence):
    """Criterio 7: el paquete permite reconstruir de dónde salió la detección."""
    package, detection, asset, _, _ = _run_flow(owner_conn, device_id, evidence)

    assert package["detection"]["evidence_id"] == evidence["evidence_id"]
    assert package["detection"]["model_id"] == service.MODEL_ID
    assert package["detection"]["model_version"] == service.MODEL_VERSION
    assert package["asset"]["asset_id"] == str(asset.asset_id)
    assert package["asset"]["status"] == "validado"
    assert package["asset_status_history"][0]["to_status"] == "validado"
    assert package["reviews"][0]["verdict"] == ACCEPTED_BY_EXPERT
    assert package["seal"]["subject_id"] == str(detection.detection_id)
    assert [e["event_type"] for e in package["trace"]][:2] == [
        ev.ASSET_INGESTED, ev.DETECTION_CREATED]


def test_synthetic_origin_travels_with_the_package(owner_conn, device_id, evidence):
    """Criterio 10: lo simulado se sigue viendo como simulado fuera de la aplicación."""
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    assert package["detection"]["origen"] == "simulado"
    assert package["asset"]["origen"] == "simulado"
    assert {e["origen"] for e in package["trace"]} == {"simulado"}


def test_external_verifier_accepts_an_untouched_package(tmp_path, owner_conn, device_id, evidence):
    """El verificador corre como proceso aparte y no importa nada de `castuo`."""
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    path = tmp_path / "paquete.json"
    path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")

    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PAQUETE ÍNTEGRO" in proc.stdout
    assert "SIMULADOS" in proc.stdout   # el aviso viaja con la evidencia


def test_changing_one_byte_breaks_the_external_verifier(tmp_path, owner_conn, device_id, evidence):
    """Criterio 11, en su forma exigente: la comprobación se hace fuera de la aplicación
    principal y sobre el contenido canónico, no sobre la mera presencia de un campo."""
    package, *_ = _run_flow(owner_conn, device_id, evidence)

    manipulado = json.loads(json.dumps(package))
    original = manipulado["detection"]["label"]
    manipulado["detection"]["label"] = original[:-1] + ("x" if original[-1] != "x" else "y")

    path = tmp_path / "manipulado.json"
    path.write_text(json.dumps(manipulado, ensure_ascii=False), encoding="utf-8")

    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "PAQUETE NO VÁLIDO" in proc.stdout
    assert "el hash del paquete no cuadra" in proc.stdout
    assert "el sello no corresponde" in proc.stdout


def test_tampering_the_chain_is_caught_by_the_external_verifier(tmp_path, owner_conn,
                                                                device_id, evidence):
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    manipulado = json.loads(json.dumps(package))
    manipulado["trace"][2]["previous_trace_hash"] = "00" * 32

    path = tmp_path / "cadena.json"
    path.write_text(json.dumps(manipulado, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "no encadena" in proc.stdout


def test_the_package_verifies_the_same_after_anchoring_the_tsa_token(tmp_path, owner_conn,
                                                                    device_id, evidence):
    """Criterio 9 visto desde fuera: anclar el token no invalida un paquete ya exportado."""
    package, detection, _, seal_id, seals = _run_flow(owner_conn, device_id, evidence)
    seals.anchor(seal_id, synthetic_token(seals.get(seal_id)["canonical_hash"]), "tsa-pruebas")

    path = tmp_path / "antes.json"
    path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert seals.get(seal_id)["canonical_hash"].hex() == package["seal"]["canonical_hash"]


def test_synthetic_image_fixture_is_usable_as_evidence(owner_conn, device_id):
    """La primera prueba tenía que funcionar con un JSON y una imagen sintética."""
    png = (FIXTURES / "parcela_sintetica.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    evidence = {"evidence_id": "ev-imagen-001", "geometry": "POINT(0 0)",
                "media_sha256": __import__("hashlib").sha256(png).hexdigest(),
                "origen": "simulado"}
    detection = DetectionRepository(owner_conn).add(
        service.infer(evidence), evidence_id=evidence["evidence_id"])
    assert detection.evidence_id == "ev-imagen-001"


def test_the_package_declares_the_canonicalisation_version(owner_conn, device_id, evidence):
    """Sin el número dentro, un paquete antiguo dejaría de verificarse el día que cambie
    el contrato, sin forma de saber por qué."""
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    assert package["canon_version"] == 1


def test_the_verifier_warns_when_there_is_no_certified_anchor(tmp_path, owner_conn,
                                                              device_id, evidence):
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    path = tmp_path / "sin_anclaje.json"
    path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert "sin anclaje certificado" in proc.stdout


def test_the_verifier_rejects_an_anchor_for_another_hash(tmp_path, owner_conn,
                                                         device_id, evidence):
    import hashlib
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    package["seal_anchors"] = [{
        "anchor_id": str(uuid.uuid4()), "authority": "tsa-falsa", "origen": "simulado",
        "tsa_token": synthetic_token(hashlib.sha256(b"otra cosa").digest()).hex(),
    }]
    path = tmp_path / "anclaje_malo.json"
    path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "certifica otro hash" in proc.stdout


def test_tampering_an_event_field_is_caught_by_the_verifier(tmp_path, owner_conn,
                                                            device_id, evidence):
    """Cambiar el actor de un evento sin tocar su payload: con la cadena anterior, que
    encadenaba solo payload_hash, esto habría pasado desapercibido."""
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    manipulado = json.loads(json.dumps(package))
    manipulado["trace"][1]["actor"] = str(uuid.uuid4())
    path = tmp_path / "actor_cambiado.json"
    path.write_text(json.dumps(manipulado, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "event_hash" in proc.stdout


def test_a_real_origin_package_carries_no_synthetic_warning(tmp_path, owner_conn,
                                                            device_id, evidence):
    """Contraste con origen real: el aviso aparece por el dato, no por costumbre."""
    package, *_ = _run_flow(owner_conn, device_id, evidence)
    fingido_real = json.loads(json.dumps(package))
    for clave in ("detection", "asset"):
        fingido_real[clave]["origen"] = "real"
    for evento in fingido_real["trace"]:
        evento["origen"] = "real"
    fingido_real["seal_anchors"] = []

    path = tmp_path / "real.json"
    path.write_text(json.dumps(fingido_real, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True)
    # El paquete deja de ser íntegro porque cambiar el origen altera el hash: eso es
    # justamente lo que debe ocurrir. Lo que se comprueba es que el aviso de simulado
    # desaparece cuando el dato dice ser real.
    assert "SIMULADOS" not in proc.stdout
