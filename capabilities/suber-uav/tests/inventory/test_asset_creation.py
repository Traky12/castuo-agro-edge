"""Inventario: alta, idempotencia e inmutabilidad campo a campo."""
from __future__ import annotations

import uuid

import psycopg
import pytest

from castuo.common.origen import Origen
from castuo.inventory.repository import InventoryRepository

pytestmark = pytest.mark.integration

INMUTABLES = {
    "asset_type": "'parcela'",
    "geometry": "'POINT(9 9)'",
    "owner_ref": "'11111111-1111-1111-1111-111111111111'::uuid",
    "source_event_id": "'otro-evento'",
    "captured_at": "now() + interval '1 day'",
    "created_at": "now() + interval '1 day'",
    "schema_version": "99",
    "origen": "'real'",
    "initial_status": "'validado'",
}


def test_asset_is_created_with_stable_identifier(owner_conn):
    repo = InventoryRepository(owner_conn)
    asset, creado = repo.ingest_asset(source_event_id="ev-001", asset_type="arbol",
                                      geometry="POINT(0 0)")
    assert creado is True
    assert repo.get(asset.asset_id).asset_id == asset.asset_id


def test_same_ingest_event_twice_does_not_create_two_assets(owner_conn):
    """Criterio 1. La idempotencia vive en el UNIQUE del esquema, no en una comprobación
    en Python que dos procesos simultáneos se saltarían."""
    repo = InventoryRepository(owner_conn)
    primero, creado_1 = repo.ingest_asset(source_event_id="ev-rep", asset_type="arbol",
                                          geometry="POINT(1 1)")
    segundo, creado_2 = repo.ingest_asset(source_event_id="ev-rep", asset_type="arbol",
                                          geometry="POINT(1 1)")
    assert (creado_1, creado_2) == (True, False)
    assert primero.asset_id == segundo.asset_id
    assert owner_conn.execute("SELECT count(*) FROM asset").fetchone()[0] == 1


@pytest.mark.parametrize("campo,valor", sorted(INMUTABLES.items()))
def test_every_asset_field_is_immutable(owner_conn, campo, valor):
    """El activo no tiene ningún campo mutable: el estado cambia por evento, no por UPDATE.
    Se prueba campo a campo para que el mensaje de error nombre el que falló."""
    asset, _ = InventoryRepository(owner_conn).ingest_asset(
        source_event_id=f"ev-{campo}", asset_type="arbol", geometry="POINT(0 0)")
    owner_conn.commit()
    antes = owner_conn.execute(
        "SELECT * FROM asset WHERE asset_id = %s", (asset.asset_id,)).fetchone()

    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_"):
        owner_conn.execute(
            f"UPDATE asset SET {campo} = {valor} WHERE asset_id = %s", (asset.asset_id,))
    owner_conn.rollback()

    despues = owner_conn.execute(
        "SELECT * FROM asset WHERE asset_id = %s", (asset.asset_id,)).fetchone()
    assert despues == antes, "la fila cambió pese a que la operación fue rechazada"


def test_synthetic_data_is_marked_as_synthetic_from_the_schema(owner_conn):
    """Criterio 10."""
    asset, _ = InventoryRepository(owner_conn).ingest_asset(
        source_event_id="ev-sint", asset_type="parcela", geometry=None,
        origen=Origen.SIMULADO)
    assert asset.origen is Origen.SIMULADO
    assert owner_conn.execute(
        "SELECT origen FROM asset WHERE asset_id = %s", (asset.asset_id,)
    ).fetchone()[0] == "simulado"
