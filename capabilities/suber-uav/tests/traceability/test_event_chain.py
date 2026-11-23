"""Cadena de trazabilidad por dispositivo."""
from __future__ import annotations

import uuid

import psycopg
import pytest

from castuo.common.hashing import hash_payload, trace_event_hash
from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.traceability.chain import BrokenChain, verify_chain
from castuo.traceability.repository import TraceRepository

pytestmark = pytest.mark.integration


def test_each_event_links_to_its_entity_and_keeps_the_previous_hash(owner_conn, device_id):
    """Criterio 6."""
    repo = TraceRepository(owner_conn)
    entity = uuid.uuid4()
    actor = uuid.uuid4()

    first = repo.append(device_id=device_id, entity_type="asset", entity_id=entity,
                        event_type="asset.ingested", actor=actor, payload={"n": 1})
    second = repo.append(device_id=device_id, entity_type="asset", entity_id=entity,
                         event_type="asset.proposed", actor=actor, payload={"n": 2})

    assert first.sequence_no == 1 and first.previous_trace_hash is None
    assert second.sequence_no == 2
    assert second.previous_trace_hash == first.event_hash
    assert second.previous_trace_hash != first.payload_hash  # se encadena el evento entero
    verify_chain(repo.for_device(device_id))


def test_two_devices_keep_independent_chains(owner_conn):
    """ADR-009: sin orden global, cada dispositivo escribe sin coordinarse con el otro."""
    repo = TraceRepository(owner_conn)
    a, b = uuid.uuid4(), uuid.uuid4()
    for device in (a, b, a, b):
        repo.append(device_id=device, entity_type="asset", entity_id=uuid.uuid4(),
                    event_type="asset.ingested", actor=uuid.uuid4(), payload={"d": str(device)})

    assert [e.sequence_no for e in repo.for_device(a)] == [1, 2]
    assert [e.sequence_no for e in repo.for_device(b)] == [1, 2]
    verify_chain(repo.for_device(a))
    verify_chain(repo.for_device(b))


def test_duplicate_sequence_for_the_same_device_is_rejected(owner_conn, device_id):
    repo = TraceRepository(owner_conn)
    first = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                        event_type="asset.ingested", actor=uuid.uuid4(), payload={"n": 1})
    owner_conn.commit()
    with pytest.raises((psycopg.errors.UniqueViolation, psycopg.errors.RestrictViolation)):
        owner_conn.execute(
            """INSERT INTO trace_event (trace_id, device_id, entity_type, entity_id, event_type,
                    actor, sequence_no, payload_hash, event_hash, previous_trace_hash,
                    schema_version, origen)
               VALUES (%s,%s,'asset',%s,'x',%s,1,%s,%s,NULL,%s,'simulado')""",
            (uuid.uuid4(), device_id, uuid.uuid4(), uuid.uuid4(),
             hash_payload({"otra": True}), hash_payload({"evento": "otro"}), SCHEMA_VERSION))
    owner_conn.rollback()


def test_wrong_previous_hash_is_rejected_by_the_engine(owner_conn, device_id):
    """El CHECK no puede mirar otra fila; esta comprobación es del trigger."""
    repo = TraceRepository(owner_conn)
    repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                event_type="asset.ingested", actor=uuid.uuid4(), payload={"n": 1})
    owner_conn.commit()
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_CHAIN"):
        owner_conn.execute(
            """INSERT INTO trace_event (trace_id, device_id, entity_type, entity_id, event_type,
                    actor, sequence_no, payload_hash, event_hash, previous_trace_hash,
                    schema_version, origen)
               VALUES (%s,%s,'asset',%s,'x',%s,2,%s,%s,%s,%s,'simulado')""",
            (uuid.uuid4(), device_id, uuid.uuid4(), uuid.uuid4(), hash_payload({"n": 2}),
             hash_payload({"evento": 2}), b"\x00" * 32, SCHEMA_VERSION))
    owner_conn.rollback()


def test_first_event_must_start_at_one(owner_conn, device_id):
    """Dos capas lo impiden: el trigger de cadena (que se ejecuta antes) y el CHECK
    `trace_first_event_has_no_previous`. La prueba acepta cualquiera de las dos porque
    lo que importa es que el motor lo rechace, no cuál de los dos guardas salta."""
    with pytest.raises((psycopg.errors.RestrictViolation, psycopg.errors.CheckViolation)):
        owner_conn.execute(
            """INSERT INTO trace_event (trace_id, device_id, entity_type, entity_id, event_type,
                    actor, sequence_no, payload_hash, event_hash, previous_trace_hash,
                    schema_version, origen)
               VALUES (%s,%s,'asset',%s,'x',%s,5,%s,%s,NULL,%s,'simulado')""",
            (uuid.uuid4(), device_id, uuid.uuid4(), uuid.uuid4(), hash_payload({"n": 5}),
             hash_payload({"evento": 5}), SCHEMA_VERSION))
    owner_conn.rollback()


def test_broken_chain_is_detected_offline_with_a_concrete_reason(owner_conn, device_id):
    """La verificación fuera del motor da el motivo, no solo un veredicto."""
    repo = TraceRepository(owner_conn)
    e1 = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                     event_type="a", actor=uuid.uuid4(), payload={"n": 1})
    e2 = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                     event_type="b", actor=uuid.uuid4(), payload={"n": 2})
    manipulado = e2.__class__(**{**e2.__dict__, "previous_trace_hash": b"\x09" * 32})
    with pytest.raises(BrokenChain, match="no encadena"):
        verify_chain([e1, manipulado])


# ---------------------------------------------------------------- event_hash completo
@pytest.mark.parametrize("campo,valor", [
    ("actor", uuid.UUID("22222222-2222-2222-2222-222222222222")),
    ("entity_id", uuid.UUID("33333333-3333-3333-3333-333333333333")),
    ("event_type", "otro.tipo"),
    ("sequence_no", 99),
    ("entity_type", "otra_entidad"),
])
def test_changing_any_event_field_invalidates_the_event_hash(owner_conn, device_id, campo, valor):
    """Encadenar solo `payload_hash` dejaría alterar los metadatos del evento sin romper la
    continuidad. Por eso se encadena el hash del evento completo, y cambiar cualquiera de
    sus campos tiene que invalidarlo."""
    repo = TraceRepository(owner_conn)
    original = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                           event_type="asset.ingested", actor=uuid.uuid4(), payload={"n": 1})

    campos = dict(device_id=original.device_id, sequence_no=original.sequence_no,
                  entity_type=original.entity_type, entity_id=original.entity_id,
                  event_type=original.event_type, actor=original.actor,
                  occurred_at=original.occurred_at, payload_hash=original.payload_hash,
                  previous_trace_hash=original.previous_trace_hash,
                  schema_version=original.schema_version, origen=original.origen.value)
    assert trace_event_hash(**campos) == original.event_hash

    campos[campo] = valor
    assert trace_event_hash(**campos) != original.event_hash


def test_changing_origen_invalidates_the_event_hash(owner_conn, device_id):
    repo = TraceRepository(owner_conn)
    e = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                    event_type="asset.ingested", actor=uuid.uuid4(), payload={"n": 1})
    campos = dict(device_id=e.device_id, sequence_no=e.sequence_no, entity_type=e.entity_type,
                  entity_id=e.entity_id, event_type=e.event_type, actor=e.actor,
                  occurred_at=e.occurred_at, payload_hash=e.payload_hash,
                  previous_trace_hash=e.previous_trace_hash,
                  schema_version=e.schema_version, origen="real")
    assert trace_event_hash(**campos) != e.event_hash


def test_verify_chain_detects_a_forged_event_hash(owner_conn, device_id):
    """No basta con comprobar el encadenado: si solo se mirara eso, se podría reescribir un
    evento y su hash a la vez. `verify_chain` recalcula cada event_hash."""
    repo = TraceRepository(owner_conn)
    e1 = repo.append(device_id=device_id, entity_type="asset", entity_id=uuid.uuid4(),
                     event_type="a", actor=uuid.uuid4(), payload={"n": 1})
    manipulado = e1.__class__(**{**e1.__dict__, "event_type": "otro"})
    with pytest.raises(BrokenChain, match="no corresponde a su contenido"):
        verify_chain([manipulado])
