"""asset_proposal: el vínculo detección → activo propuesto.

Existe porque la detección es inmutable: si `asset_id` es nulo al crearla, el vínculo no
puede escribirse encima después.
"""
from __future__ import annotations

import json
import pathlib
import uuid

import psycopg
import pytest

from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.detection import service
from castuo.detection.repository import DetectionRepository
from castuo.inventory.repository import InventoryRepository

pytestmark = pytest.mark.integration
FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures/synthetic/vuelo_sintetico.json"


@pytest.fixture
def contexto(owner_conn):
    evidencia = json.loads(FIXTURE.read_text(encoding="utf-8"))
    deteccion = DetectionRepository(owner_conn).add(
        service.infer(evidencia), evidence_id=evidencia["evidence_id"])
    activo, _ = InventoryRepository(owner_conn).ingest_asset(
        source_event_id=f"ev-{uuid.uuid4()}", asset_type="arbol", geometry="POINT(0 0)")
    return deteccion, activo


def test_detection_can_exist_without_asset_and_propose_one_later(owner_conn, contexto):
    deteccion, activo = contexto
    repo = DetectionRepository(owner_conn)
    assert deteccion.asset_id is None

    _, creada = repo.propose_asset(deteccion.detection_id, activo.asset_id)
    assert creada is True
    assert repo.assets_for(deteccion.detection_id) == [activo.asset_id]


def test_the_proposal_does_not_modify_the_detection(owner_conn, contexto):
    deteccion, activo = contexto
    repo = DetectionRepository(owner_conn)
    antes = owner_conn.execute(
        "SELECT * FROM detection WHERE detection_id = %s", (deteccion.detection_id,)).fetchone()
    repo.propose_asset(deteccion.detection_id, activo.asset_id)
    despues = owner_conn.execute(
        "SELECT * FROM detection WHERE detection_id = %s", (deteccion.detection_id,)).fetchone()
    assert antes == despues


def test_repeating_the_same_proposal_is_idempotent(owner_conn, contexto):
    deteccion, activo = contexto
    repo = DetectionRepository(owner_conn)
    primera, creada_1 = repo.propose_asset(deteccion.detection_id, activo.asset_id)
    segunda, creada_2 = repo.propose_asset(deteccion.detection_id, activo.asset_id)
    assert (creada_1, creada_2) == (True, False)
    assert primera == segunda
    assert owner_conn.execute("SELECT count(*) FROM asset_proposal").fetchone()[0] == 1


def test_a_detection_can_propose_several_assets(owner_conn, contexto):
    deteccion, activo = contexto
    inventario = InventoryRepository(owner_conn)
    repo = DetectionRepository(owner_conn)
    otro, _ = inventario.ingest_asset(source_event_id=f"ev-{uuid.uuid4()}",
                                      asset_type="arbol", geometry="POINT(2 2)")
    repo.propose_asset(deteccion.detection_id, activo.asset_id)
    repo.propose_asset(deteccion.detection_id, otro.asset_id)
    assert set(repo.assets_for(deteccion.detection_id)) == {activo.asset_id, otro.asset_id}


@pytest.mark.parametrize("columna", ["detection_id", "asset_id", "origen", "schema_version"])
def test_mandatory_columns_reject_null(owner_conn, contexto, columna):
    deteccion, activo = contexto
    valores = {"proposal_id": uuid.uuid4(), "detection_id": deteccion.detection_id,
               "asset_id": activo.asset_id, "schema_version": SCHEMA_VERSION,
               "origen": Origen.SIMULADO.value}
    valores[columna] = None
    with pytest.raises((psycopg.errors.NotNullViolation, psycopg.errors.InvalidTextRepresentation)):
        owner_conn.execute(
            """INSERT INTO asset_proposal (proposal_id, detection_id, asset_id,
                    schema_version, origen) VALUES (%s,%s,%s,%s,%s)""",
            (valores["proposal_id"], valores["detection_id"], valores["asset_id"],
             valores["schema_version"], valores["origen"]))
    owner_conn.rollback()


@pytest.mark.parametrize("columna", ["detection_id", "asset_id"])
def test_foreign_keys_are_enforced(owner_conn, contexto, columna):
    deteccion, activo = contexto
    detection_id = uuid.uuid4() if columna == "detection_id" else deteccion.detection_id
    asset_id = uuid.uuid4() if columna == "asset_id" else activo.asset_id
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        owner_conn.execute(
            """INSERT INTO asset_proposal (proposal_id, detection_id, asset_id,
                    schema_version, origen) VALUES (%s,%s,%s,%s,'simulado')""",
            (uuid.uuid4(), detection_id, asset_id, SCHEMA_VERSION))
    owner_conn.rollback()
