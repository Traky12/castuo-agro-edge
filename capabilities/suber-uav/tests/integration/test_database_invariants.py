"""Primera prueba de aceptación del slice: la base de datos es inmutable.

Va antes que la detección a propósito. Si esta propiedad no se demuestra, todo lo que venga
después puede producir evidencia de aspecto impecable sobre un almacén reescribible.

Se comprueban las dos capas por separado —permisos del rol de aplicación y triggers— y las
tres operaciones —UPDATE, DELETE y TRUNCATE—, con tablas llenas y vacías. Que la fila siga
ahí después de cada intento fallido se verifica explícitamente: un rechazo que dejara el
dato a medias no serviría de nada.
"""
from __future__ import annotations

import uuid

import psycopg
import pytest

from castuo.common.hashing import hash_payload, trace_event_hash
from castuo.common.origen import SCHEMA_VERSION, Origen

pytestmark = pytest.mark.integration

APPEND_ONLY = ["asset", "asset_status_event", "detection", "asset_proposal",
               "review", "seal", "seal_anchor", "trace_event"]
OPERACIONES = {
    "UPDATE":   "UPDATE {t} SET schema_version = schema_version",
    "DELETE":   "DELETE FROM {t}",
    "TRUNCATE": "TRUNCATE TABLE {t} CASCADE",
}


def _insert_asset(conn, source_event_id="ev-1"):
    asset_id = uuid.uuid4()
    conn.execute(
        """INSERT INTO asset (asset_id, asset_type, geometry, initial_status,
                              source_event_id, captured_at, schema_version, origen)
           VALUES (%s, 'arbol', 'POINT(0 0)', 'detectado', %s, now(), %s, %s)""",
        (asset_id, source_event_id, SCHEMA_VERSION, Origen.SIMULADO.value))
    return asset_id


def _insert_detection(conn, asset_id=None):
    detection_id = uuid.uuid4()
    conn.execute(
        """INSERT INTO detection (detection_id, asset_id, evidence_id, model_id,
                model_version, label, confidence, geometry, params, input_hash,
                result_hash, schema_version, origen)
           VALUES (%s,%s,'ev-1','ranking-sintetico','0.1.0','prioridad_alta',0.87,
                   'POINT(0 0)','{}'::jsonb,%s,%s,%s,%s)""",
        (detection_id, asset_id, hash_payload({"a": 1}), hash_payload({"b": 2}),
         SCHEMA_VERSION, Origen.SIMULADO.value))
    return detection_id


def _seed_all(conn):
    """Siembra una fila en cada tabla append-only.

    Sin datos, un trigger de fila no se dispara y la prueba pasaría por vacuidad: fue
    exactamente el fallo que destapó la necesidad de los triggers de sentencia.
    """
    asset_id = _insert_asset(conn)
    detection_id = _insert_detection(conn, asset_id)
    actor = uuid.uuid4()

    conn.execute(
        """INSERT INTO asset_status_event (status_event_id, asset_id, sequence_no, from_status,
                to_status, actor, schema_version, origen)
           VALUES (%s,%s,1,'detectado','validado',%s,%s,'simulado')""",
        (uuid.uuid4(), asset_id, actor, SCHEMA_VERSION))
    conn.execute(
        """INSERT INTO asset_proposal (proposal_id, detection_id, asset_id,
                schema_version, origen)
           VALUES (%s,%s,%s,%s,'simulado')""",
        (uuid.uuid4(), detection_id, asset_id, SCHEMA_VERSION))

    seal_id = uuid.uuid4()
    conn.execute(
        """INSERT INTO seal (seal_id, subject_type, subject_id, canonical_hash,
                schema_version, origen)
           VALUES (%s,'detection',%s,%s,%s,'simulado')""",
        (seal_id, detection_id, hash_payload({"c": 3}), SCHEMA_VERSION))
    conn.execute(
        """INSERT INTO review (review_id, detection_id, verdict, review_type, actor,
                seal_id, schema_version, origen)
           VALUES (%s,%s,'accepted_by_expert','expert',%s,%s,%s,'simulado')""",
        (uuid.uuid4(), detection_id, actor, seal_id, SCHEMA_VERSION))
    conn.execute(
        """INSERT INTO seal_anchor (anchor_id, seal_id, tsa_token, authority,
                schema_version, origen)
           VALUES (%s,%s,%s,'autoridad-de-pruebas',%s,'simulado')""",
        (uuid.uuid4(), seal_id, b"token-sintetico", SCHEMA_VERSION))

    device_id, occurred = uuid.uuid4(), None
    from datetime import datetime, timezone
    occurred = datetime.now(timezone.utc)
    payload_hash = hash_payload({"d": 4})
    event_hash = trace_event_hash(
        device_id=device_id, sequence_no=1, entity_type="detection", entity_id=detection_id,
        event_type="detection.created", actor=actor, occurred_at=occurred,
        payload_hash=payload_hash, previous_trace_hash=None,
        schema_version=SCHEMA_VERSION, origen="simulado")
    conn.execute(
        """INSERT INTO trace_event (trace_id, device_id, entity_type, entity_id, event_type,
                actor, sequence_no, occurred_at, payload_hash, event_hash,
                previous_trace_hash, schema_version, origen)
           VALUES (%s,%s,'detection',%s,'detection.created',%s,1,%s,%s,%s,NULL,%s,'simulado')""",
        (uuid.uuid4(), device_id, detection_id, actor, occurred, payload_hash,
         event_hash, SCHEMA_VERSION))
    return asset_id, detection_id, seal_id


# --------------------------------------------------------------- capa 1: permisos
@pytest.mark.parametrize("tabla", APPEND_ONLY)
@pytest.mark.parametrize("privilegio", ["UPDATE", "DELETE", "TRUNCATE"])
def test_app_role_lacks_the_privilege(owner_conn, tabla, privilegio):
    concedido = owner_conn.execute(
        "SELECT has_table_privilege('castuo_app', %s, %s)", (tabla, privilegio)
    ).fetchone()[0]
    assert concedido is False, f"castuo_app no debería tener {privilegio} sobre {tabla}"


@pytest.mark.parametrize("operacion", list(OPERACIONES))
def test_app_role_is_blocked_by_permissions(owner_conn, app_conn, operacion):
    _seed_all(owner_conn)
    owner_conn.commit()
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        app_conn.execute(OPERACIONES[operacion].format(t="detection"))
    app_conn.rollback()
    assert owner_conn.execute("SELECT count(*) FROM detection").fetchone()[0] == 1


# --------------------------------------------------------------- capa 2: triggers
@pytest.mark.parametrize("tabla", APPEND_ONLY)
@pytest.mark.parametrize("operacion", list(OPERACIONES))
def test_trigger_rejects_the_operation_even_for_the_owner(owner_conn, tabla, operacion):
    """Aunque los permisos fallaran, el motor rechaza con un error explícito."""
    _seed_all(owner_conn)
    owner_conn.commit()
    antes = owner_conn.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0]

    with pytest.raises(psycopg.errors.RestrictViolation,
                       match="CASTUO_APPEND_ONLY|CASTUO_IMMUTABLE_FIELD"):
        owner_conn.execute(OPERACIONES[operacion].format(t=tabla))
    owner_conn.rollback()

    # La fila sigue intacta tras el intento fallido.
    assert owner_conn.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0] == antes == 1


@pytest.mark.parametrize("tabla", APPEND_ONLY)
@pytest.mark.parametrize("operacion", list(OPERACIONES))
def test_empty_table_also_rejects_the_operation(owner_conn, tabla, operacion):
    """Un trigger de fila no se dispara sin filas: sin los de sentencia, esto pasaría."""
    assert owner_conn.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0] == 0
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_APPEND_ONLY"):
        owner_conn.execute(OPERACIONES[operacion].format(t=tabla))
    owner_conn.rollback()


def test_origen_is_mandatory_everywhere(owner_conn):
    with pytest.raises(psycopg.errors.NotNullViolation):
        owner_conn.execute(
            """INSERT INTO asset (asset_id, asset_type, initial_status, source_event_id,
                                  captured_at, schema_version, origen)
               VALUES (%s,'arbol','detectado','ev-x',now(),%s,NULL)""",
            (uuid.uuid4(), SCHEMA_VERSION))
    owner_conn.rollback()
