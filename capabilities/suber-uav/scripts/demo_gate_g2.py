#!/usr/bin/env python3
"""Ensayo en seco del gate G2: contraste ciego de principio a fin.

Reproduce con datos sintéticos lo que ocurrirá en febrero de 2027 en la parcela real:
se pacta el umbral, el sistema ordena, se congela y se sella, y solo entonces entra el
orden del corchero. La concordancia se calcula con la métrica y el listón del protocolo,
no con los que elija quien ejecute esto.

    python3 scripts/demo_gate_g2.py

Salida: el veredicto y, sobre todo, la prueba de que el orden del experto no podía
entrar antes del sello.
"""
from __future__ import annotations

import pathlib
import sys
import uuid
from decimal import Decimal

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import psycopg

from castuo.common.origen import SCHEMA_VERSION
from castuo.ranking import service
from castuo.ranking.repository import ContrastRepository
from castuo.storage.connection import connect_owner

UNIDADES = [
    {"unit_ref": "rodal-A", "perimetro_rel": 0.81, "altura_rel": 0.62},
    {"unit_ref": "rodal-B", "perimetro_rel": 0.44, "altura_rel": 0.51},
    {"unit_ref": "rodal-C", "perimetro_rel": 0.93, "altura_rel": 0.77},
    {"unit_ref": "rodal-D", "perimetro_rel": 0.20, "altura_rel": 0.35},
    {"unit_ref": "rodal-E", "perimetro_rel": 0.67, "altura_rel": 0.71},
]

# El corchero ordena a ciegas. En este ensayo coincide casi del todo, con un intercambio.
ORDEN_EXPERTO = {"rodal-C": 1, "rodal-A": 2, "rodal-E": 3, "rodal-D": 4, "rodal-B": 5}


def main() -> int:
    conn = connect_owner()
    repo = ContrastRepository(conn)

    print("1. PROTOCOLO — se pacta antes de que exista ningún dato")
    protocolo = repo.register_protocol(
        scope_ref="finca-demo/parcela-1", unit_kind="rodal", metric="spearman",
        threshold=Decimal("0.70000"), registered_by=uuid.uuid4())
    p = repo.protocol(protocolo)
    print(f"   metrica={p['metric']}  umbral={p['threshold']}  unidad={p['unit_kind']}\n")

    print("2. ORDEN DEL SISTEMA")
    resultado = service.rank(UNIDADES)
    ranking_id = repo.store_ranking(resultado, protocol_id=protocolo)
    for item in resultado["items"]:
        print(f"   {item['position']}. {item['unit_ref']}  score={item['score']}")
    print(f"   content_hash={resultado['content_hash'].hex()[:32]}...\n")

    print("3. EL MURO — intento de cargar el orden del experto SIN sellar")
    try:
        repo.store_expert_ranking(ranking_id=ranking_id, actor=uuid.uuid4(),
                                  orden=ORDEN_EXPERTO)
        print("   ¡ERROR! la carga fue aceptada; el muro no está funcionando")
        return 1
    except psycopg.errors.RestrictViolation as exc:
        # No hace falta rollback: la escritura va en su propio punto de guardado, así que
        # el ranking del paso 2 sigue en pie.
        print(f"   rechazado por el motor: {str(exc).splitlines()[0]}\n")

    print("4. SELLO LOCAL")
    seal_id = uuid.uuid4()
    conn.execute(
        """INSERT INTO seal (seal_id, subject_type, subject_id, canonical_hash,
                    seal_kind, schema_version, origen)
           VALUES (%s,'ranking',%s,%s,'local',%s,'simulado')""",
        (seal_id, ranking_id, resultado["content_hash"], SCHEMA_VERSION))
    print(f"   seal_id={seal_id}\n")

    print("5. ORDEN DEL EXPERTO — ahora sí")
    experto = repo.store_expert_ranking(ranking_id=ranking_id, actor=uuid.uuid4(),
                                        orden=ORDEN_EXPERTO)
    for unidad, posicion in sorted(ORDEN_EXPERTO.items(), key=lambda kv: kv[1]):
        print(f"   {posicion}. {unidad}")
    print()

    print("6. CONCORDANCIA")
    medida = repo.compute_concordance(ranking_id=ranking_id, expert_ranking_id=experto)
    conn.commit()
    print(f"   {medida['metric']} v{medida['metric_version']} = {medida['value']}")
    print(f"   umbral aplicado (del protocolo) = {medida['threshold_applied']}")
    print(f"   VEREDICTO: {medida['verdict'].upper()}\n")

    print("Todos los datos de este ensayo son SIMULADOS y están marcados como tales en el")
    print("esquema. No constituyen evidencia de campo.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
