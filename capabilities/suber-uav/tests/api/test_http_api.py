"""API HTTP contra PostgreSQL real.

No se simula la base de datos: las invariantes que importan viven en el motor, y una API
probada contra dobles demostraría que el código llama a lo que cree llamar, no que el
sistema conserva lo que dice conservar.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from castuo.api.app import app
from castuo.api.auth import CABECERA, enrolar, revocar

pytestmark = pytest.mark.integration

UNIDADES = [
    {"unit_ref": "rodal-A", "perimetro_rel": 0.81, "altura_rel": 0.62},
    {"unit_ref": "rodal-B", "perimetro_rel": 0.44, "altura_rel": 0.51},
    {"unit_ref": "rodal-C", "perimetro_rel": 0.93, "altura_rel": 0.77},
    {"unit_ref": "rodal-D", "perimetro_rel": 0.20, "altura_rel": 0.35},
]


@pytest.fixture
def cliente(owner_conn):
    """La API comparte la conexión de la prueba para que ambas vean el mismo esquema."""
    app.state.conn_factory = lambda: owner_conn
    app.state.close_conn = False
    yield TestClient(app)
    app.state.conn_factory = None


@pytest.fixture
def clave(owner_conn):
    _, clave = enrolar(owner_conn, label="pi-de-pruebas")
    return clave


def cab(clave):
    return {CABECERA: clave}


# ------------------------------------------------------------------- autenticación
def test_health_needs_no_credential(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200 and r.json()["entorno"] == "sintetico"


@pytest.mark.parametrize("cabeceras", [{}, {CABECERA: "clave-inventada"}])
def test_writing_without_a_valid_credential_is_rejected(cliente, cabeceras):
    r = cliente.post("/v1/evidence", json={"source_event_id": "ev-1", "asset_type": "arbol"},
                     headers=cabeceras)
    assert r.status_code == 401


def test_the_error_does_not_distinguish_missing_from_invalid(cliente, clave):
    """Distinguirlos regalaría información a quien esté probando claves."""
    sin = cliente.post("/v1/evidence", json={"source_event_id": "a", "asset_type": "arbol"})
    mala = cliente.post("/v1/evidence", json={"source_event_id": "a", "asset_type": "arbol"},
                        headers=cab("otra"))
    assert sin.json() == mala.json()


def test_a_revoked_device_loses_access(cliente, owner_conn, clave):
    device_id, clave_2 = enrolar(owner_conn, label="pi-a-revocar")
    assert cliente.post("/v1/evidence", json={"source_event_id": "ev-r", "asset_type": "arbol"},
                        headers=cab(clave_2)).status_code == 201
    revocar(owner_conn, device_id)
    assert cliente.post("/v1/evidence", json={"source_event_id": "ev-r2", "asset_type": "arbol"},
                        headers=cab(clave_2)).status_code == 401


def test_the_api_key_is_never_stored_in_clear(owner_conn):
    _, clave = enrolar(owner_conn, label="pi-x")
    en_claro = owner_conn.execute(
        "SELECT count(*) FROM device WHERE encode(api_key_hash,'escape') = %s", (clave,)
    ).fetchone()[0]
    assert en_claro == 0


# ------------------------------------------------------------------- ingesta
def test_ingesting_the_same_evidence_twice_is_idempotent(cliente, clave):
    cuerpo = {"source_event_id": "ev-http-1", "asset_type": "parcela",
              "geometry": "POINT(0 0)"}
    primera = cliente.post("/v1/evidence", json=cuerpo, headers=cab(clave))
    segunda = cliente.post("/v1/evidence", json=cuerpo, headers=cab(clave))

    assert primera.status_code == 201 and primera.json()["creado"] is True
    assert segunda.status_code == 201 and segunda.json()["creado"] is False
    assert primera.json()["asset_id"] == segunda.json()["asset_id"]


def test_ingesting_writes_one_trace_event_not_two(cliente, owner_conn, clave):
    """El reintento no debe ensuciar la cadena con un evento por intento."""
    cuerpo = {"source_event_id": "ev-http-2", "asset_type": "arbol"}
    cliente.post("/v1/evidence", json=cuerpo, headers=cab(clave))
    cliente.post("/v1/evidence", json=cuerpo, headers=cab(clave))
    eventos = owner_conn.execute(
        "SELECT count(*) FROM trace_event WHERE event_type = 'asset.ingested'").fetchone()[0]
    assert eventos == 1


def test_every_write_lands_on_the_chain_of_the_authenticated_device(cliente, owner_conn):
    device_id, clave_d = enrolar(owner_conn, label="pi-cadena")
    cliente.post("/v1/evidence", json={"source_event_id": "ev-cad", "asset_type": "arbol"},
                 headers=cab(clave_d))
    fila = owner_conn.execute(
        "SELECT device_id, sequence_no FROM trace_event ORDER BY occurred_at DESC LIMIT 1"
    ).fetchone()
    assert fila[0] == device_id and fila[1] == 1


# ------------------------------------------------------------------- detección
def test_detection_is_deterministic_over_http(cliente, clave):
    cuerpo = {"evidence_id": "ev-det", "evidence": {"a": 1, "geometry": "POINT(1 1)"}}
    primera = cliente.post("/v1/detections", json=cuerpo, headers=cab(clave)).json()
    segunda = cliente.post("/v1/detections", json=cuerpo, headers=cab(clave)).json()
    assert primera["result_hash"] == segunda["result_hash"]
    assert primera["detection_id"] != segunda["detection_id"]   # append-only, no sobrescribe


# ------------------------------------------------------------------- el muro, por HTTP
def _protocolo(cliente, clave, umbral="0.7"):
    return cliente.post("/v1/protocols", headers=cab(clave), json={
        "scope_ref": "parcela-1", "unit_kind": "rodal", "metric": "spearman",
        "threshold": umbral}).json()["protocol_id"]


def _ranking(cliente, clave, protocol_id):
    return cliente.post("/v1/rankings", headers=cab(clave),
                        json={"protocol_id": protocol_id, "unidades": UNIDADES}).json()


def test_the_expert_order_is_refused_with_409_before_the_seal(cliente, clave):
    protocolo = _protocolo(cliente, clave)
    ranking = _ranking(cliente, clave, protocolo)
    r = cliente.post(f"/v1/rankings/{ranking['ranking_id']}/expert-order", headers=cab(clave),
                     json={"orden": {"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4}})
    assert r.status_code == 409
    assert "CASTUO_BLIND" in r.json()["detail"]


def test_the_full_contrast_over_http_gives_a_verdict(cliente, clave):
    protocolo = _protocolo(cliente, clave)
    ranking = _ranking(cliente, clave, protocolo)
    ranking_id = ranking["ranking_id"]
    assert ranking["orden"][0]["unit_ref"] == "rodal-C"

    sello = cliente.post(f"/v1/rankings/{ranking_id}/seal", headers=cab(clave))
    assert sello.status_code == 201
    assert sello.json()["anclaje_certificado"] is None      # el contrato lo dice, no lo oculta

    experto = cliente.post(f"/v1/rankings/{ranking_id}/expert-order", headers=cab(clave),
                           json={"orden": {"rodal-C": 1, "rodal-A": 2,
                                           "rodal-B": 3, "rodal-D": 4}})
    assert experto.status_code == 201

    concordancia = cliente.post(
        f"/v1/rankings/{ranking_id}/concordance", headers=cab(clave),
        params={"expert_ranking_id": experto.json()["expert_ranking_id"]})
    cuerpo = concordancia.json()
    assert concordancia.status_code == 201
    assert cuerpo["verdict"] == "supera"
    assert Decimal(cuerpo["threshold_applied"]) == Decimal("0.7")


def test_the_caller_cannot_choose_the_threshold_at_computation_time(cliente, clave):
    """Se registra un umbral imposible de superar y se comprueba que manda el protocolo."""
    protocolo = _protocolo(cliente, clave, umbral="0.99")
    ranking = _ranking(cliente, clave, protocolo)
    ranking_id = ranking["ranking_id"]
    cliente.post(f"/v1/rankings/{ranking_id}/seal", headers=cab(clave))
    experto = cliente.post(f"/v1/rankings/{ranking_id}/expert-order", headers=cab(clave),
                           json={"orden": {"rodal-C": 1, "rodal-A": 2,
                                           "rodal-B": 4, "rodal-D": 3}}).json()
    cuerpo = cliente.post(f"/v1/rankings/{ranking_id}/concordance", headers=cab(clave),
                          params={"expert_ranking_id": experto["expert_ranking_id"]}).json()
    assert Decimal(cuerpo["threshold_applied"]) == Decimal("0.99")
    assert cuerpo["verdict"] == "no_supera"


def test_a_ranking_of_one_unit_is_rejected_with_422(cliente, clave):
    protocolo = _protocolo(cliente, clave)
    r = cliente.post("/v1/rankings", headers=cab(clave),
                     json={"protocol_id": protocolo, "unidades": [UNIDADES[0]]})
    assert r.status_code == 422


def test_reading_a_ranking_says_whether_it_is_sealed(cliente, clave):
    protocolo = _protocolo(cliente, clave)
    ranking_id = _ranking(cliente, clave, protocolo)["ranking_id"]
    assert cliente.get(f"/v1/rankings/{ranking_id}", headers=cab(clave)).json()["sellado"] is False
    cliente.post(f"/v1/rankings/{ranking_id}/seal", headers=cab(clave))
    assert cliente.get(f"/v1/rankings/{ranking_id}", headers=cab(clave)).json()["sellado"] is True


# ------------------------------------------------------------------- verificador como servicio
def test_the_verifier_service_runs_the_same_script_a_third_party_would(cliente, clave):
    paquete = {"canon_version": 99, "package_hash": "x"}
    r = cliente.post("/v1/verify", json=paquete, headers=cab(clave))
    assert r.status_code == 200
    assert r.json()["integro"] is False
    assert "canonicalización no soportada" in r.json()["errores"][0]
