"""Capa de captura: misión, observación y reidentificación (gate G1 en seco)."""
from __future__ import annotations

import uuid
from decimal import Decimal

import psycopg
import pytest

from castuo.common.origen import Origen
from castuo.uav.models import ESCALERA, Payload, peldano
from castuo.uav.reidentificacion import (
    GeometriaNoSoportada,
    METRIC_VERSION,
    reidentificar,
)
from castuo.uav.repository import MissionRepository, ObservationRepository


# ------------------------------------------------------------------ escalera
def test_la_escalera_de_carga_util_tiene_orden_estable():
    assert [p.value for p in ESCALERA] == [
        "P0_rgb", "P1_rgb_rtk", "P2_multiespectral", "P3_lidar"]
    assert peldano(Payload.P0_RGB) < peldano(Payload.P2_MULTIESPECTRAL)


# ------------------------------------------------------------------ misión
@pytest.mark.integration
def test_la_mision_se_ingiere_una_sola_vez(app_conn):
    repo = MissionRepository(app_conn)
    args = dict(source_event_id="mision-001", forest_ref="rodal-A", aircraft="banco",
                payload=Payload.P0_RGB, operator=uuid.uuid4(), extractor_version="0.1.0")
    m1, creada1 = repo.ingest_mission(**args)
    m2, creada2 = repo.ingest_mission(**args)
    assert creada1 is True and creada2 is False
    assert m1.mission_id == m2.mission_id


@pytest.mark.integration
def test_una_mision_real_sin_autorizacion_de_vuelo_se_rechaza(app_conn):
    repo = MissionRepository(app_conn)
    with pytest.raises(psycopg.errors.CheckViolation):
        repo.ingest_mission(
            source_event_id="mision-real-sin-permiso", forest_ref="rodal-A",
            aircraft="uav", payload=Payload.P0_RGB, operator=uuid.uuid4(),
            extractor_version="0.1.0", origen=Origen.REAL)


@pytest.mark.integration
def test_una_mision_real_con_autorizacion_se_admite(app_conn):
    repo = MissionRepository(app_conn)
    m, creada = repo.ingest_mission(
        source_event_id="mision-real-con-permiso", forest_ref="rodal-A", aircraft="uav",
        payload=Payload.P0_RGB, operator=uuid.uuid4(), extractor_version="0.1.0",
        authorization_ref="AESA-XXXX", origen=Origen.REAL)
    assert creada is True and m.origen is Origen.REAL


@pytest.mark.integration
def test_la_mision_no_se_puede_modificar_ni_borrar(owner_conn):
    with owner_conn.cursor() as cur:
        with pytest.raises(psycopg.errors.RestrictViolation):
            cur.execute("UPDATE uav_mission SET aircraft = 'otro'")
    owner_conn.rollback()
    with owner_conn.cursor() as cur:
        with pytest.raises(psycopg.errors.RestrictViolation):
            cur.execute("DELETE FROM uav_mission")
    owner_conn.rollback()
    # TRUNCATE se rechaza por dos motivos distintos y ambos valen: la clave ajena de
    # `uav_observation` lo impide antes incluso de que llegue a dispararse el trigger de
    # sentencia. Se afirma sobre el rechazo, no sobre cuál de las dos capas lo produjo.
    with owner_conn.cursor() as cur:
        with pytest.raises((psycopg.errors.RestrictViolation,
                            psycopg.errors.FeatureNotSupported)):
            cur.execute("TRUNCATE uav_mission")
    owner_conn.rollback()
    with owner_conn.cursor() as cur:
        with pytest.raises((psycopg.errors.RestrictViolation,
                            psycopg.errors.FeatureNotSupported)):
            cur.execute("TRUNCATE uav_observation")
    owner_conn.rollback()


# ------------------------------------------------------------------ observación
def _mision(conn, sufijo: str = "") -> uuid.UUID:
    m, _ = MissionRepository(conn).ingest_mission(
        source_event_id=f"mision{sufijo}", forest_ref="rodal-A", aircraft="banco",
        payload=Payload.P0_RGB, operator=uuid.uuid4(), extractor_version="0.1.0")
    return m.mission_id


@pytest.mark.integration
def test_la_observacion_es_idempotente_por_unidad(app_conn):
    mid = _mision(app_conn)
    repo = ObservationRepository(app_conn)
    args = dict(mission_id=mid, unit_ref="A-001", descriptors={"perimetro_rel": 0.8},
                quality=Decimal("0.9"), extractor_version="0.1.0",
                geometry="POINT(10 20)")
    o1, c1 = repo.record(**args)
    o2, c2 = repo.record(**args)
    assert c1 is True and c2 is False
    assert o1.observation_id == o2.observation_id


@pytest.mark.integration
def test_la_observacion_puede_nacer_sin_arbol_asignado(app_conn):
    mid = _mision(app_conn)
    obs, _ = ObservationRepository(app_conn).record(
        mission_id=mid, unit_ref="A-002", descriptors={}, quality=Decimal("0.5"),
        extractor_version="0.1.0", geometry="POINT(0 0)")
    assert obs.asset_id is None


@pytest.mark.integration
def test_la_deteccion_puede_referenciar_la_observacion_de_la_que_salio(app_conn):
    mid = _mision(app_conn)
    obs, _ = ObservationRepository(app_conn).record(
        mission_id=mid, unit_ref="A-003", descriptors={}, quality=Decimal("1.0"),
        extractor_version="0.1.0", geometry="POINT(1 1)")
    fila = app_conn.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'detection' AND column_name = 'observation_id'").fetchone()
    assert fila is not None, "detection debe poder apuntar a la observación (incoherencia 6)"
    assert obs.observation_id is not None


# ------------------------------------------------------------------ reidentificación
class _Obs:
    def __init__(self, unit_ref, geometry):
        self.unit_ref = unit_ref
        self.geometry = geometry


def test_la_tolerancia_es_obligatoria_y_positiva():
    with pytest.raises(ValueError):
        reidentificar([], [], tolerancia_m=0)


def test_reencuentro_perfecto_con_desplazamiento_dentro_de_tolerancia():
    a = [_Obs("A-1", "POINT(0 0)"), _Obs("A-2", "POINT(10 0)")]
    b = [_Obs("B-1", "POINT(0.3 0.1)"), _Obs("B-2", "POINT(10.2 0)")]
    r = reidentificar(a, b, tolerancia_m=1.0)
    assert r.metric_version == METRIC_VERSION
    assert r.tasa_reencuentro == 1.0
    assert r.jaccard == 1.0
    assert r.solo_en_a == () and r.solo_en_b == ()
    assert r.desviacion_media_m < 0.4


def test_un_pie_fuera_de_tolerancia_no_se_empareja():
    a = [_Obs("A-1", "POINT(0 0)"), _Obs("A-2", "POINT(10 0)")]
    b = [_Obs("B-1", "POINT(0.1 0)")]
    r = reidentificar(a, b, tolerancia_m=1.0)
    assert r.tasa_reencuentro == 0.5
    assert r.solo_en_a == ("A-2",)
    assert r.solo_en_b == ()


def test_el_emparejamiento_es_simetrico():
    a = [_Obs("A-1", "POINT(0 0)"), _Obs("A-2", "POINT(1.2 0)")]
    b = [_Obs("B-1", "POINT(0.5 0)")]
    ab = reidentificar(a, b, tolerancia_m=2.0)
    ba = reidentificar(b, a, tolerancia_m=2.0)
    assert len(ab.emparejadas) == len(ba.emparejadas) == 1
    assert ab.emparejadas[0].unit_a == "A-1"
    assert ba.emparejadas[0].unit_b == "A-1"


def test_ningun_pie_se_empareja_dos_veces():
    a = [_Obs("A-1", "POINT(0 0)")]
    b = [_Obs("B-1", "POINT(0.1 0)"), _Obs("B-2", "POINT(0.2 0)")]
    r = reidentificar(a, b, tolerancia_m=5.0)
    assert len(r.emparejadas) == 1
    assert r.solo_en_b == ("B-2",)


def test_una_observacion_sin_geometria_no_se_reidentifica():
    with pytest.raises(GeometriaNoSoportada):
        reidentificar([_Obs("A-1", None)], [_Obs("B-1", "POINT(0 0)")], tolerancia_m=1.0)


def test_una_geometria_que_no_es_punto_se_rechaza():
    with pytest.raises(GeometriaNoSoportada):
        reidentificar([_Obs("A-1", "LINESTRING(0 0, 1 1)")],
                      [_Obs("B-1", "POINT(0 0)")], tolerancia_m=1.0)


def test_el_resultado_no_depende_del_orden_de_entrada():
    a = [_Obs("A-2", "POINT(10 0)"), _Obs("A-1", "POINT(0 0)")]
    b = [_Obs("B-2", "POINT(10.1 0)"), _Obs("B-1", "POINT(0.1 0)")]
    r1 = reidentificar(a, b, tolerancia_m=1.0)
    r2 = reidentificar(list(reversed(a)), list(reversed(b)), tolerancia_m=1.0)
    assert r1.emparejadas == r2.emparejadas


@pytest.mark.integration
def test_g1_en_seco_sobre_dos_misiones_persistidas(app_conn):
    """El gate G1 recorrido de punta a punta con datos sintéticos."""
    repo_o = ObservationRepository(app_conn)
    m1 = _mision(app_conn, "-g1-a")
    m2 = _mision(app_conn, "-g1-b")
    for i in range(10):
        repo_o.record(mission_id=m1, unit_ref=f"U-{i:03d}", descriptors={"i": i},
                      quality=Decimal("0.9"), extractor_version="0.1.0",
                      geometry=f"POINT({i * 5} 0)")
        # Mismo rodal, segundo vuelo: desplazamiento pequeño, salvo un pie que se pierde.
        if i != 7:
            repo_o.record(mission_id=m2, unit_ref=f"V-{i:03d}", descriptors={"i": i},
                          quality=Decimal("0.9"), extractor_version="0.1.0",
                          geometry=f"POINT({i * 5 + 0.4} 0.2)")

    r = reidentificar(repo_o.by_mission(m1), repo_o.by_mission(m2), tolerancia_m=1.0)
    assert r.total_a == 10 and r.total_b == 9
    assert len(r.emparejadas) == 9
    assert r.solo_en_a == ("U-007",)
    assert r.tasa_reencuentro == pytest.approx(0.9)
