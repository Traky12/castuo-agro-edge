"""Estado del activo: transiciones declaradas, registradas como eventos.

`status` dejó de ser una columna mutable. La consecuencia práctica es que el rol de
aplicación no necesita UPDATE en ninguna tabla, y que cada cambio de estado guarda quién
lo hizo y cuándo, que es lo que un auditor va a pedir.
"""
from __future__ import annotations

import uuid

import psycopg
import pytest

from castuo.inventory.repository import InventoryRepository
from castuo.inventory.status import TRANSICIONES, AssetStatusRepository

pytestmark = pytest.mark.integration

VALIDAS = sorted(TRANSICIONES)
INVALIDAS = [("detectado", "detectado"), ("validado", "detectado"),
             ("descartado", "validado"), ("descartado", "detectado"),
             ("validado", "pendiente")]


@pytest.fixture
def asset(owner_conn):
    a, _ = InventoryRepository(owner_conn).ingest_asset(
        source_event_id=f"ev-{uuid.uuid4()}", asset_type="arbol", geometry="POINT(0 0)")
    return a


def test_initial_status_is_projected_when_there_are_no_events(owner_conn, asset):
    assert AssetStatusRepository(owner_conn).current(asset.asset_id) == "detectado"


@pytest.mark.parametrize("desde,hasta", VALIDAS)
def test_declared_transitions_are_accepted(owner_conn, desde, hasta):
    inventario = InventoryRepository(owner_conn)
    estados = AssetStatusRepository(owner_conn)
    a, _ = inventario.ingest_asset(source_event_id=f"ev-{desde}-{hasta}",
                                   asset_type="arbol", geometry=None,
                                   initial_status=desde)
    evento = estados.transition(asset_id=a.asset_id, to_status=hasta, actor=uuid.uuid4(),
                                reason="prueba")
    assert evento.from_status == desde and evento.to_status == hasta
    assert estados.current(a.asset_id) == hasta


@pytest.mark.parametrize("desde,hasta", INVALIDAS)
def test_undeclared_transitions_are_rejected(owner_conn, desde, hasta):
    inventario = InventoryRepository(owner_conn)
    estados = AssetStatusRepository(owner_conn)
    a, _ = inventario.ingest_asset(source_event_id=f"ev-mal-{desde}-{hasta}",
                                   asset_type="arbol", geometry=None,
                                   initial_status=desde)
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_STATUS"):
        estados.transition(asset_id=a.asset_id, to_status=hasta, actor=uuid.uuid4())
    owner_conn.rollback()


def test_an_event_that_starts_from_a_stale_status_is_rejected(owner_conn, asset):
    """Si dos personas deciden a la vez sobre el mismo activo, la segunda no puede partir
    de un estado que ya no es el vigente."""
    estados = AssetStatusRepository(owner_conn)
    estados.transition(asset_id=asset.asset_id, to_status="validado", actor=uuid.uuid4())
    with pytest.raises(psycopg.errors.RestrictViolation, match="estado vigente"):
        owner_conn.execute(
            """INSERT INTO asset_status_event (status_event_id, asset_id, sequence_no,
                    from_status, to_status, actor, schema_version, origen)
               VALUES (%s,%s,2,'detectado','descartado',%s,1,'simulado')""",
            (uuid.uuid4(), asset.asset_id, uuid.uuid4()))
    owner_conn.rollback()


def test_the_history_keeps_who_and_when(owner_conn, asset):
    estados = AssetStatusRepository(owner_conn)
    actor = uuid.uuid4()
    estados.transition(asset_id=asset.asset_id, to_status="validado", actor=actor,
                       reason="contrastado en campo")
    estados.transition(asset_id=asset.asset_id, to_status="descartado", actor=actor,
                       reason="duplicado")
    historial = estados.history(asset.asset_id)
    assert [(e.from_status, e.to_status) for e in historial] == [
        ("detectado", "validado"), ("validado", "descartado")]
    assert all(e.actor == actor for e in historial)
    assert historial[1].reason == "duplicado"


def test_two_transitions_in_the_same_transaction_keep_their_order(owner_conn, asset):
    """Regresión: `now()` devuelve la hora de la TRANSACCIÓN, así que dos transiciones
    escritas sin commit intermedio comparten `occurred_at`. Ordenar por hora dejaba el
    estado vigente a merced del UUID. El orden lo fija `sequence_no`."""
    estados = AssetStatusRepository(owner_conn)
    estados.transition(asset_id=asset.asset_id, to_status="validado", actor=uuid.uuid4())
    estados.transition(asset_id=asset.asset_id, to_status="descartado", actor=uuid.uuid4())

    historial = estados.history(asset.asset_id)
    assert [e.sequence_no for e in historial] == [1, 2]
    assert len({e.occurred_at for e in historial}) == 1, "misma transacción, misma hora"
    assert estados.current(asset.asset_id) == "descartado"
