"""El contraste ciego, de principio a fin.

La propiedad que se demuestra aquí es la que sostiene el gate G2: el orden del sistema se
congela y se sella antes de que exista el orden del experto, y el umbral se fija antes de
que exista ningún dato. Las dos cosas las impone el motor, no el procedimiento.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import psycopg
import pytest

from castuo.export.seal import SealRepository
from castuo.ranking import service
from castuo.ranking.repository import ContrastRepository

pytestmark = pytest.mark.integration

UNIDADES = [
    {"unit_ref": "rodal-A", "perimetro_rel": 0.81, "altura_rel": 0.62},
    {"unit_ref": "rodal-B", "perimetro_rel": 0.44, "altura_rel": 0.51},
    {"unit_ref": "rodal-C", "perimetro_rel": 0.93, "altura_rel": 0.77},
    {"unit_ref": "rodal-D", "perimetro_rel": 0.20, "altura_rel": 0.35},
]


class SelloDeRanking(SealRepository):
    """El sello de un ranking usa el mismo mecanismo que el de una detección: lo que
    cambia es el sujeto."""

    def seal_ranking(self, ranking_id, content_hash, origen_valor="simulado"):
        from castuo.common.origen import SCHEMA_VERSION
        seal_id = uuid.uuid4()
        self.conn.execute(
            """INSERT INTO seal (seal_id, subject_type, subject_id, canonical_hash,
                        seal_kind, schema_version, origen)
               VALUES (%s,'ranking',%s,%s,'local',%s,%s)""",
            (seal_id, ranking_id, content_hash, SCHEMA_VERSION, origen_valor))
        return seal_id


@pytest.fixture
def protocolo(owner_conn):
    """El protocolo se registra primero: métrica y umbral pactados sin datos delante."""
    return ContrastRepository(owner_conn).register_protocol(
        scope_ref="finca-alburquerque/parcela-1", unit_kind="rodal", metric="spearman",
        threshold=Decimal("0.70000"), registered_by=uuid.uuid4())


@pytest.fixture
def ranking(owner_conn, protocolo):
    repo = ContrastRepository(owner_conn)
    return repo.store_ranking(service.rank(UNIDADES), protocol_id=protocolo)


def test_the_system_order_is_deterministic(owner_conn):
    """Dos ejecuciones sobre las mismas unidades dan el mismo orden y el mismo hash,
    aunque las unidades lleguen desordenadas."""
    primera = service.rank(UNIDADES)
    segunda = service.rank(list(reversed(UNIDADES)))
    assert primera["content_hash"] == segunda["content_hash"]
    assert [i["unit_ref"] for i in primera["items"]] == [i["unit_ref"] for i in segunda["items"]]


def test_the_order_puts_the_strongest_unit_first(owner_conn, ranking):
    posiciones = ContrastRepository(owner_conn).positions(ranking)
    assert posiciones["rodal-C"] == 1     # el de mayor perímetro y altura
    assert posiciones["rodal-D"] == 4     # el menor


def test_the_expert_order_cannot_be_loaded_before_the_seal(owner_conn, ranking):
    """El muro. Es la respuesta a «¿cómo sé que no ajustasteis el modelo después de ver
    al corchero?», y vive en el motor."""
    repo = ContrastRepository(owner_conn)
    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_BLIND"):
        repo.store_expert_ranking(ranking_id=ranking, actor=uuid.uuid4(),
                                  orden={"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4})
    owner_conn.rollback()


def test_after_sealing_the_expert_order_is_accepted(owner_conn, ranking):
    repo = ContrastRepository(owner_conn)
    sellos = SelloDeRanking(owner_conn)
    sellos.seal_ranking(ranking, repo.ranking(ranking)["content_hash"])

    experto = repo.store_expert_ranking(
        ranking_id=ranking, actor=uuid.uuid4(),
        orden={"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4})
    assert repo.expert_positions(experto)["rodal-C"] == 1


def test_the_threshold_comes_from_the_protocol_not_from_the_caller(owner_conn, ranking):
    """Nadie puede elegir el listón al calcular: se copia del protocolo registrado antes."""
    repo = ContrastRepository(owner_conn)
    SelloDeRanking(owner_conn).seal_ranking(ranking, repo.ranking(ranking)["content_hash"])
    experto = repo.store_expert_ranking(
        ranking_id=ranking, actor=uuid.uuid4(),
        orden={"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4})

    resultado = repo.compute_concordance(ranking_id=ranking, expert_ranking_id=experto)
    assert resultado["threshold_applied"] == Decimal("0.70000")
    assert resultado["metric"] == "spearman"
    assert resultado["verdict"] == "supera"


def test_a_poor_agreement_produces_a_negative_verdict(owner_conn, protocolo):
    """El sistema tiene que poder decir que NO supera: si solo supiera aprobar, el gate
    no serviría de nada."""
    repo = ContrastRepository(owner_conn)
    ranking = repo.store_ranking(service.rank(UNIDADES), protocol_id=protocolo)
    SelloDeRanking(owner_conn).seal_ranking(ranking, repo.ranking(ranking)["content_hash"])

    inverso = {u: p for u, p in zip(
        [i["unit_ref"] for i in repo.ranking(ranking)["items"]], [4, 3, 2, 1])}
    experto = repo.store_expert_ranking(ranking_id=ranking, actor=uuid.uuid4(), orden=inverso)

    resultado = repo.compute_concordance(ranking_id=ranking, expert_ranking_id=experto)
    assert resultado["value"] == Decimal("-1")
    assert resultado["verdict"] == "no_supera"


def test_the_same_expert_cannot_load_two_orders_for_one_ranking(owner_conn, ranking):
    """Permitirlo dejaría reintentar hasta acertar."""
    repo = ContrastRepository(owner_conn)
    SelloDeRanking(owner_conn).seal_ranking(ranking, repo.ranking(ranking)["content_hash"])
    actor = uuid.uuid4()
    orden = {"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4}
    repo.store_expert_ranking(ranking_id=ranking, actor=actor, orden=orden)
    owner_conn.commit()
    with pytest.raises(psycopg.errors.UniqueViolation):
        repo.store_expert_ranking(ranking_id=ranking, actor=actor, orden=orden)
    owner_conn.rollback()


def test_a_second_run_of_the_model_is_a_new_ranking_not_an_overwrite(owner_conn, protocolo):
    """Reajustar el modelo sigue siendo legítimo; lo que no puede es pasar inadvertido."""
    repo = ContrastRepository(owner_conn)
    primero = repo.store_ranking(service.rank(UNIDADES), protocol_id=protocolo)
    SelloDeRanking(owner_conn).seal_ranking(primero, repo.ranking(primero)["content_hash"])
    repo.store_expert_ranking(ranking_id=primero, actor=uuid.uuid4(),
                              orden={"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4})

    otros_pesos = service.rank(UNIDADES, params={"pesos": {"perimetro_rel": 0.1,
                                                          "altura_rel": 0.9}},
                               model_version="0.2.0")
    segundo = repo.store_ranking(otros_pesos, protocol_id=protocolo)

    assert segundo != primero
    assert repo.ranking(primero)["model_version"] == "0.1.0"
    assert repo.ranking(segundo)["model_version"] == "0.2.0"
    assert repo.ranking(primero)["content_hash"] != repo.ranking(segundo)["content_hash"]


@pytest.mark.parametrize("tabla", ["contrast_protocol", "ranking", "ranking_item",
                                   "expert_ranking", "expert_ranking_item", "concordance"])
def test_the_contrast_tables_are_append_only(owner_conn, tabla):
    for operacion in (f"UPDATE {tabla} SET schema_version = schema_version",
                      f"DELETE FROM {tabla}", f"TRUNCATE TABLE {tabla} CASCADE"):
        with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_APPEND_ONLY"):
            owner_conn.execute(operacion)
        owner_conn.rollback()


def test_hitting_the_wall_does_not_destroy_the_caller_transaction(owner_conn, protocolo):
    """Chocar contra el muro es un resultado esperado del protocolo, no un accidente:
    no puede llevarse por delante el trabajo ya hecho en la misma transacción."""
    repo = ContrastRepository(owner_conn)
    ranking = repo.store_ranking(service.rank(UNIDADES), protocol_id=protocolo)

    with pytest.raises(psycopg.errors.RestrictViolation, match="CASTUO_BLIND"):
        repo.store_expert_ranking(ranking_id=ranking, actor=uuid.uuid4(),
                                  orden={"rodal-C": 1, "rodal-A": 2,
                                         "rodal-B": 3, "rodal-D": 4})

    # Sin rollback: el ranking sigue existiendo y el flujo puede continuar.
    assert repo.ranking(ranking)["ranking_id"] == ranking
    SelloDeRanking(owner_conn).seal_ranking(ranking, repo.ranking(ranking)["content_hash"])
    experto = repo.store_expert_ranking(
        ranking_id=ranking, actor=uuid.uuid4(),
        orden={"rodal-C": 1, "rodal-A": 2, "rodal-B": 3, "rodal-D": 4})
    assert repo.compute_concordance(ranking_id=ranking,
                                    expert_ranking_id=experto)["verdict"] == "supera"
