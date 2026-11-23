"""Reproducibilidad del hash de resultado.

Es la propiedad que permite decir a un tercero «esto se puede volver a calcular». Si el
hash cubriera tiempos o identificadores generados, dos ejecuciones idénticas darían
resultados distintos y la afirmación sería falsa.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from castuo.common.hashing import NON_DETERMINISTIC, detection_result_hash
from castuo.common.origen import Origen
from castuo.detection import service

FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures/synthetic/vuelo_sintetico.json"
EVIDENCE = json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_same_input_model_and_params_give_the_same_result_hash():
    """Criterio 4."""
    a = service.infer(EVIDENCE, params={"umbral": 2})
    b = service.infer(EVIDENCE, params={"umbral": 2})
    assert a["result_hash"] == b["result_hash"]
    assert a["label"] == b["label"] and a["confidence"] == b["confidence"]


def test_key_order_in_params_does_not_change_the_hash():
    a = service.infer(EVIDENCE, params={"umbral": 1, "modo": "estricto"})
    b = service.infer(EVIDENCE, params={"modo": "estricto", "umbral": 1})
    assert a["result_hash"] == b["result_hash"]


@pytest.mark.parametrize("campo", ["model_version", "origen", "input_hash", "params"])
def test_changing_a_determinant_field_changes_the_result_hash(campo):
    """Prueba negativa pedida: alterar model_version, origen, input_hash o params
    tiene que alterar el hash. Si no, el hash no está cubriendo lo que dice cubrir."""
    base = dict(input_hash=b"\x11" * 32, model_id="m", model_version="1.0",
                params={"umbral": 1}, label="prioridad_alta", confidence="0.5",
                geometry=None, origen="simulado")
    original = detection_result_hash(**base)

    alterado = dict(base)
    alterado[campo] = {
        "model_version": "1.1",
        "origen": "real",
        "input_hash": b"\x22" * 32,
        "params": {"umbral": 2},
    }[campo]

    assert detection_result_hash(**alterado) != original


def test_non_deterministic_fields_are_declared_and_excluded():
    """Los campos no deterministas están nombrados en un solo sitio, para que nadie
    los añada al contenido hasheado por descuido."""
    for campo in ("detected_at", "detection_id", "sealed_at", "trace_id"):
        assert campo in NON_DETERMINISTIC
