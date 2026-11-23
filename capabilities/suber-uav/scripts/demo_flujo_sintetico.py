#!/usr/bin/env python3
"""Ejecuta el flujo sintético completo y deja el paquete en disco.

    python3 scripts/demo_flujo_sintetico.py salida.json
    python3 scripts/verify_package.py salida.json
"""
import json, pathlib, sys, uuid
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tests"))
from castuo.storage.connection import connect_owner
from integration.test_full_synthetic_flow import _run_flow, FIXTURES

destino = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "paquete_sintetico.json")
evidence = json.loads((FIXTURES / "vuelo_sintetico.json").read_text(encoding="utf-8"))
conn = connect_owner()
paquete, deteccion, activo, seal_id, _ = _run_flow(conn, uuid.uuid4(), evidence)
conn.commit()
destino.write_text(json.dumps(paquete, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"activo    {activo.asset_id} ({paquete['asset']['status']}, origen={activo.origen.value})")
print(f"deteccion {deteccion.detection_id} {deteccion.label} conf={deteccion.confidence}")
print(f"sello     {seal_id}")
print(f"paquete   {destino} ({len(paquete['trace'])} eventos de traza)")
