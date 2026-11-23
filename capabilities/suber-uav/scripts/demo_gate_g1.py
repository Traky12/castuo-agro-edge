#!/usr/bin/env python3
"""Ensayo en seco del gate G1 — captura repetible.

Regla del proyecto: ningún gate se intenta en campo antes de que su ensayo en seco pase
con datos sintéticos. Este guion recorre G1 de punta a punta —dos misiones sobre el mismo
rodal, reidentificación, veredicto contra una tolerancia pactada de antemano— sin un solo
dispositivo real.

Lo que este guion **no** demuestra: que el vuelo real produzca esos descriptores. Solo que
el sistema sabe registrar dos misiones, compararlas y emitir un veredicto reproducible.

Uso:
    python3 scripts/demo_gate_g1.py [--pies 60] [--tolerancia 1.0] [--deriva 0.35]
"""
from __future__ import annotations

import argparse
import random
import sys
import uuid
from decimal import Decimal

from castuo.common.origen import Origen
from castuo.storage.connection import connect_app
from castuo.uav.models import Payload
from castuo.uav.reidentificacion import reidentificar
from castuo.uav.repository import MissionRepository, ObservationRepository

SEMILLA = 20270301          # semilla fija: el ensayo es reproducible o no es un ensayo
EXTRACTOR = "descriptor-sintetico/0.1.0"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pies", type=int, default=60)
    p.add_argument("--tolerancia", type=float, default=1.0,
                   help="metros; en campo se pacta en F0 antes de mirar el dato (A-02)")
    p.add_argument("--deriva", type=float, default=0.35,
                   help="desviación típica del desplazamiento simulado entre vuelos")
    p.add_argument("--perdidos", type=int, default=3,
                   help="pies que el segundo vuelo no ve, para que el ensayo no sea trivial")
    args = p.parse_args()

    rnd = random.Random(SEMILLA)
    marca = uuid.uuid4().hex[:8]

    print("=" * 74)
    print("ENSAYO EN SECO — GATE G1 · captura repetible")
    print("=" * 74)
    print(f"  Datos           : SIMULADOS (origen = 'simulado'), semilla {SEMILLA}")
    print(f"  Pies del rodal  : {args.pies}")
    print(f"  Tolerancia      : {args.tolerancia:.2f} m  [pactada ANTES de generar el dato]")
    print(f"  Deriva simulada : {args.deriva:.2f} m")
    print(f"  Pies perdidos   : {args.perdidos}")
    print()

    conn = connect_app()
    conn.autocommit = True
    misiones = MissionRepository(conn)
    obs = ObservationRepository(conn)

    operador = uuid.uuid4()
    m1, _ = misiones.ingest_mission(
        source_event_id=f"g1-{marca}-vuelo-1", forest_ref=f"rodal-ensayo-{marca}",
        aircraft="banco de ensayo", payload=Payload.P0_RGB, operator=operador,
        extractor_version=EXTRACTOR, planned_agl_m=Decimal("60.00"),
        overlap_pct=Decimal("80.00"), origen=Origen.SIMULADO)
    m2, _ = misiones.ingest_mission(
        source_event_id=f"g1-{marca}-vuelo-2", forest_ref=f"rodal-ensayo-{marca}",
        aircraft="banco de ensayo", payload=Payload.P0_RGB, operator=operador,
        extractor_version=EXTRACTOR, planned_agl_m=Decimal("60.00"),
        overlap_pct=Decimal("80.00"), origen=Origen.SIMULADO)
    print(f"  Misión 1 : {m1.mission_id}  carga útil {m1.payload.value}")
    print(f"  Misión 2 : {m2.mission_id}  carga útil {m2.payload.value}")
    print()

    # Rodal sintético: pies en malla irregular pero determinista.
    pies = [(rnd.uniform(0, 120), rnd.uniform(0, 120)) for _ in range(args.pies)]
    perdidos = set(rnd.sample(range(args.pies), min(args.perdidos, args.pies)))

    for i, (x, y) in enumerate(pies):
        obs.record(mission_id=m1.mission_id, unit_ref=f"P1-{i:03d}",
                   descriptors={"perimetro_rel": round(rnd.uniform(0.3, 1.0), 4)},
                   quality=Decimal("0.95"), extractor_version=EXTRACTOR,
                   geometry=f"POINT({x:.4f} {y:.4f})", origen=Origen.SIMULADO)
        if i in perdidos:
            continue
        dx, dy = rnd.gauss(0, args.deriva), rnd.gauss(0, args.deriva)
        obs.record(mission_id=m2.mission_id, unit_ref=f"P2-{i:03d}",
                   descriptors={"perimetro_rel": round(rnd.uniform(0.3, 1.0), 4)},
                   quality=Decimal("0.95"), extractor_version=EXTRACTOR,
                   geometry=f"POINT({x + dx:.4f} {y + dy:.4f})", origen=Origen.SIMULADO)

    r = reidentificar(obs.by_mission(m1.mission_id), obs.by_mission(m2.mission_id),
                      tolerancia_m=args.tolerancia)

    print("-" * 74)
    print("RESULTADO")
    print("-" * 74)
    print(f"  Método               : vecino mutuo más cercano v{r.metric_version}")
    print(f"  Pies vuelo 1 / 2     : {r.total_a} / {r.total_b}")
    print(f"  Emparejados          : {len(r.emparejadas)}")
    print(f"  Tasa de reencuentro  : {r.tasa_reencuentro:.4f}")
    print(f"  Jaccard              : {r.jaccard:.4f}")
    print(f"  Desviación media     : {r.desviacion_media_m:.3f} m")
    print(f"  Solo en el vuelo 1   : {len(r.solo_en_a)}")
    print(f"  Solo en el vuelo 2   : {len(r.solo_en_b)}")
    print()

    # El umbral del gate real se pacta en F0 con el protocolo. Aquí se usa solo para
    # comprobar que el ensayo distingue un resultado bueno de uno malo.
    umbral_ensayo = (args.pies - args.perdidos) / args.pies - 0.02
    supera = r.tasa_reencuentro >= umbral_ensayo
    print(f"  Umbral del ENSAYO    : {umbral_ensayo:.4f}   [NO es el umbral de G1]")
    print(f"  Veredicto del ensayo : {'PASA' if supera else 'NO PASA'}")
    print()
    print("  [EVIDENCIA NO PERSISTIDA] El resultado de G1 todavía no se registra como")
    print("  evidencia sellada: eso es UMD-2. Este ensayo imprime, no asienta.")
    print("  [PENDIENTE F0] Tolerancia real, sistema de referencia y umbral de G1.")
    return 0 if supera else 1


if __name__ == "__main__":
    sys.exit(main())
