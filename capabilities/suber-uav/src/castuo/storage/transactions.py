"""Unidad de trabajo.

La cadena de trazabilidad se valida contra la última fila del dispositivo, así que dos
escrituras simultáneas del mismo dispositivo podrían calcular el mismo `sequence_no`.
El bloqueo de aviso por dispositivo serializa esa sección crítica sin bloquear tablas
enteras: dos dispositivos distintos siguen escribiendo en paralelo.
"""
from __future__ import annotations

import uuid
from contextlib import contextmanager

import psycopg

_DEVICE_LOCK_NAMESPACE = 0x0CA5


@contextmanager
def unit_of_work(conn: psycopg.Connection):
    with conn.transaction():
        yield conn


@contextmanager
def device_chain_lock(conn: psycopg.Connection, device_id: uuid.UUID):
    """Serializa las escrituras de la cadena de un dispositivo dentro de la transacción."""
    with conn.transaction():
        conn.execute(
            "SELECT pg_advisory_xact_lock(%s, hashtext(%s))",
            (_DEVICE_LOCK_NAMESPACE, str(device_id)),
        )
        yield conn
