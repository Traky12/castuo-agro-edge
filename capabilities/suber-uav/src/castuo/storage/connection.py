"""Conexión a PostgreSQL.

Dos roles distintos a propósito: el propietario aplica migraciones, y la aplicación
corre con un rol sin UPDATE ni DELETE. Que la propia librería ofrezca ambos hace visible
en el código qué operaciones necesitan privilegio de esquema.
"""
from __future__ import annotations

import os

import psycopg

DEFAULT_HOST = os.environ.get("CASTUO_PGHOST", "localhost")
DEFAULT_PORT = os.environ.get("CASTUO_PGPORT", "5432")
DEFAULT_DB = os.environ.get("CASTUO_PGDATABASE", "castuo_test")


def _dsn(user: str) -> str:
    return f"host={DEFAULT_HOST} port={DEFAULT_PORT} dbname={DEFAULT_DB} user={user}"


def connect_owner() -> psycopg.Connection:
    """Conexión con privilegios de esquema. Solo para migraciones y pruebas."""
    return psycopg.connect(_dsn(os.environ.get("CASTUO_PGOWNER", "postgres")))


def connect_app() -> psycopg.Connection:
    """Conexión de la aplicación: sin UPDATE ni DELETE por permisos."""
    return psycopg.connect(_dsn(os.environ.get("CASTUO_PGAPPUSER", "castuo_app")))
