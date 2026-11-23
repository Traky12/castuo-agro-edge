"""La cadena no se puede reescribir.

Complementa `tests/integration/test_database_invariants.py`, que cubre las tablas
append-only en bloque; aquí se comprueba lo específico de la traza: que ni siquiera el
propietario del esquema pueda alterar un eslabón ya escrito.
"""
from __future__ import annotations

import uuid

import psycopg
import pytest

from castuo.traceability.repository import TraceRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def evento(owner_conn, device_id):
    ev = TraceRepository(owner_conn).append(
        device_id=device_id, entity_type="detection", entity_id=uuid.uuid4(),
        event_type="detection.created", actor=uuid.uuid4(), payload={"x": 1})
    owner_conn.commit()
    return ev


def test_trace_event_cannot_be_updated(owner_conn, evento):
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_APPEND_ONLY"):
        owner_conn.execute("UPDATE trace_event SET event_type = 'otro' WHERE trace_id = %s",
                           (evento.trace_id,))
    owner_conn.rollback()


def test_trace_event_cannot_be_deleted(owner_conn, evento):
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_APPEND_ONLY"):
        owner_conn.execute("DELETE FROM trace_event WHERE trace_id = %s", (evento.trace_id,))
    owner_conn.rollback()


def test_payload_hash_cannot_be_rewritten(owner_conn, evento):
    """Reescribir el hash es la forma más silenciosa de romper una cadena; por eso se
    prueba explícitamente y no solo el UPDATE genérico."""
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_APPEND_ONLY"):
        owner_conn.execute("UPDATE trace_event SET payload_hash = %s WHERE trace_id = %s",
                           (b"\x00" * 32, evento.trace_id))
    owner_conn.rollback()


def test_the_app_role_has_no_way_to_do_it_either(owner_conn, app_conn, evento):
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        app_conn.execute("DELETE FROM trace_event")
    app_conn.rollback()
