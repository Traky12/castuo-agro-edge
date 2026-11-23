"""Infraestructura de pruebas.

Cada prueba corre sobre un esquema recreado desde las migraciones: si una invariante
solo existiera en el código de la aplicación y no en el motor, aquí se vería.
"""
from __future__ import annotations

import pathlib
import uuid

import pytest

from castuo.storage.connection import connect_app, connect_owner

MIGRATIONS = sorted((pathlib.Path(__file__).resolve().parents[1] / "migrations").glob("*.sql"))


def _reset(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        cur.execute("GRANT USAGE ON SCHEMA public TO castuo_app;")
        for path in MIGRATIONS:
            cur.execute(path.read_text(encoding="utf-8"))
    conn.commit()


@pytest.fixture(scope="function")
def owner_conn():
    conn = connect_owner()
    conn.autocommit = False
    _reset(conn)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def app_conn(owner_conn):
    """Conexión con el rol de la aplicación: sin UPDATE ni DELETE."""
    conn = connect_app()
    yield conn
    conn.close()


@pytest.fixture
def device_id():
    return uuid.uuid4()
