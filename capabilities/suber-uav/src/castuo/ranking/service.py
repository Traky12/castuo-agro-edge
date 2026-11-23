"""Ordenación de unidades a partir de descriptores.

El modelo es deterministo y sintético. Lo que este slice tiene que demostrar no es que el
orden sea bueno —eso lo dirá el corchero en el gate G2— sino que el mismo conjunto de
descriptores, el mismo modelo y los mismos parámetros producen exactamente el mismo orden,
y que ese orden queda congelado antes de conocer el del experto.

Los empates se rompen por `unit_ref` para que el resultado no dependa del orden en que
lleguen las unidades: dos ejecuciones sobre el mismo lote deben coincidir hasta el último
puesto, o la reproducibilidad sería solo aparente.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Sequence

from castuo.common.canonical import sha256_bytes

MODEL_ID = "orden-prioridad-sintetico"
MODEL_VERSION = "0.1.0"

#: Pesos por defecto. Son una decisión de diseño provisional, no un resultado medido:
#: el reparto real se ajusta cuando haya datos de campo. [POR MEDIR EN F2]
PESOS_POR_DEFECTO = {"perimetro_rel": 0.6, "altura_rel": 0.4}


class DescriptoresInvalidos(ValueError):
    pass


def score(descriptores: dict[str, Any], pesos: dict[str, float]) -> Decimal:
    """Suma ponderada de los descriptores declarados en los pesos."""
    faltan = [k for k in pesos if k not in descriptores]
    if faltan:
        raise DescriptoresInvalidos(f"faltan descriptores en la unidad: {sorted(faltan)}")
    total = sum(Decimal(str(descriptores[k])) * Decimal(str(peso)) for k, peso in pesos.items())
    return total.quantize(Decimal("0.000001"))


def rank(unidades: Sequence[dict[str, Any]], *, params: dict | None = None,
         model_version: str = MODEL_VERSION) -> dict:
    """Devuelve el orden completo: posición 1 = mayor prioridad.

    El resultado incluye `content_hash`, calculado sobre lo que determina el orden —modelo,
    versión, parámetros y la lista de (unidad, posición, puntuación)— y nada más. Ese hash
    es lo que después se sella.
    """
    if not model_version or not model_version.strip():
        raise DescriptoresInvalidos("model_version es obligatorio")
    if len({u["unit_ref"] for u in unidades}) != len(unidades):
        raise DescriptoresInvalidos("hay unidades repetidas en la entrada")
    if len(unidades) < 2:
        raise DescriptoresInvalidos("un orden de menos de dos unidades no se puede contrastar")

    params = params or {}
    pesos = params.get("pesos", PESOS_POR_DEFECTO)

    puntuadas = [(u["unit_ref"], score(u, pesos)) for u in unidades]
    # Mayor puntuación primero; empates por unit_ref para que el orden no dependa de la
    # entrada.
    puntuadas.sort(key=lambda par: (-par[1], par[0]))

    items = [{"unit_ref": ref, "position": i, "score": valor}
             for i, (ref, valor) in enumerate(puntuadas, start=1)]

    content_hash = sha256_bytes({
        "model_id": MODEL_ID, "model_version": model_version, "params": params,
        "items": items,
    })
    return {"model_id": MODEL_ID, "model_version": model_version, "params": params,
            "items": items, "content_hash": content_hash}
