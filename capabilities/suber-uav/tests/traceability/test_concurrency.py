"""Concurrencia sobre la cadena de un mismo dispositivo.

El `sequence_no` y el `previous_trace_hash` se calculan leyendo el último evento del
dispositivo. Sin serialización, dos transacciones simultáneas leerían el mismo «último» y
calcularían el mismo número: una de las dos rompería la cadena o chocaría contra la
unicidad. El bloqueo de aviso por dispositivo cierra esa ventana sin bloquear tablas
enteras, de modo que dos dispositivos distintos siguen escribiendo en paralelo.
"""
from __future__ import annotations

import threading
import uuid

import psycopg
import pytest

from castuo.common.hashing import hash_payload
from castuo.common.origen import SCHEMA_VERSION
from castuo.storage.connection import connect_owner
from castuo.traceability.chain import verify_chain
from castuo.traceability.repository import TraceRepository

pytestmark = pytest.mark.integration

EVENTOS_POR_HILO = 8


def _escribir(device_id, entity_id, n, errores):
    """Cada hilo con su propia conexión: son transacciones de verdad, no simuladas."""
    try:
        conn = connect_owner()
        try:
            repo = TraceRepository(conn)
            for i in range(n):
                repo.append(device_id=device_id, entity_type="asset", entity_id=entity_id,
                            event_type="asset.ingested", actor=uuid.uuid4(),
                            payload={"hilo": str(threading.get_ident()), "i": i})
                conn.commit()
        finally:
            conn.close()
    except Exception as exc:                      # se recoge para fallar en el hilo principal
        errores.append(exc)


def test_two_concurrent_writers_on_the_same_device_keep_one_clean_chain(owner_conn, device_id):
    owner_conn.commit()
    entity_id = uuid.uuid4()
    errores: list[Exception] = []

    hilos = [threading.Thread(target=_escribir, args=(device_id, entity_id,
                                                      EVENTOS_POR_HILO, errores))
             for _ in range(2)]
    for h in hilos: h.start()
    for h in hilos: h.join(timeout=30)

    assert not errores, f"algún hilo falló: {errores}"

    eventos = TraceRepository(owner_conn).for_device(device_id)
    secuencias = [e.sequence_no for e in eventos]

    assert len(eventos) == EVENTOS_POR_HILO * 2
    assert len(set(secuencias)) == len(secuencias), "hay sequence_no repetidos"
    assert secuencias == list(range(1, EVENTOS_POR_HILO * 2 + 1)), "hay huecos en la cadena"

    for anterior, actual in zip(eventos, eventos[1:]):
        assert actual.previous_trace_hash == anterior.event_hash

    verify_chain(eventos)


def test_two_devices_write_independent_chains_concurrently(owner_conn):
    owner_conn.commit()
    a, b = uuid.uuid4(), uuid.uuid4()
    entity_id = uuid.uuid4()
    errores: list[Exception] = []

    hilos = [threading.Thread(target=_escribir, args=(d, entity_id, EVENTOS_POR_HILO, errores))
             for d in (a, b)]
    for h in hilos: h.start()
    for h in hilos: h.join(timeout=30)
    assert not errores, f"algún hilo falló: {errores}"

    repo = TraceRepository(owner_conn)
    for dispositivo in (a, b):
        eventos = repo.for_device(dispositivo)
        assert [e.sequence_no for e in eventos] == list(range(1, EVENTOS_POR_HILO + 1))
        verify_chain(eventos)


def test_the_unique_constraint_is_the_last_barrier(owner_conn, device_id):
    """Si alguien escribiera saltándose el bloqueo —otro proceso, un script suelto—, la
    unicidad (device_id, sequence_no) sigue impidiendo dos eventos con el mismo número."""
    repo = TraceRepository(owner_conn)
    primero = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                          event_type="a", actor=uuid.uuid4(), payload={"n": 1})
    owner_conn.commit()

    with pytest.raises((psycopg.errors.UniqueViolation, psycopg.errors.RestrictViolation)):
        owner_conn.execute(
            """INSERT INTO trace_event (trace_id, device_id, entity_type, entity_id,
                    event_type, actor, sequence_no, payload_hash, event_hash,
                    previous_trace_hash, schema_version, origen)
               VALUES (%s,%s,'asset',%s,'a',%s,%s,%s,%s,NULL,%s,'simulado')""",
            (uuid.uuid4(), device_id, uuid.uuid4(), uuid.uuid4(), primero.sequence_no,
             hash_payload({"n": 9}), hash_payload({"e": 9}), SCHEMA_VERSION))
    owner_conn.rollback()


def test_the_device_lock_lives_inside_the_transaction(owner_conn, device_id):
    """`pg_advisory_xact_lock` se libera al terminar la transacción, no antes ni después:
    si se liberase antes, la ventana volvería a abrirse; si no se liberase, un fallo
    dejaría el dispositivo bloqueado para siempre."""
    from castuo.storage.transactions import device_chain_lock

    with device_chain_lock(owner_conn, device_id):
        tomados = owner_conn.execute(
            "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'").fetchone()[0]
        assert tomados >= 1
    owner_conn.commit()

    tras_commit = owner_conn.execute(
        "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'").fetchone()[0]
    assert tras_commit == 0
