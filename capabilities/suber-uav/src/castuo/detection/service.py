"""Servicio de detección.

El modelo de este slice es sintético y determinista a propósito: lo que hay que demostrar
no es la calidad de una inferencia, sino que el sistema conserva de dónde salió, con qué
modelo y que el mismo trabajo repetido da el mismo resultado. Un modelo real entra después
por la misma interfaz.
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from castuo.common.hashing import detection_result_hash, hash_payload
from castuo.common.origen import Origen

MODEL_ID = "ranking-sintetico"
MODEL_VERSION = "0.1.0"
LABELS = ("prioridad_baja", "prioridad_media", "prioridad_alta")


class MissingModelVersion(ValueError):
    """Una inferencia sin versión de modelo no es reproducible ni auditable."""


def evidence_input_hash(evidence: dict[str, Any]) -> bytes:
    """Huella de la entrada. Es lo que permite decir después qué dato originó la detección."""
    return hash_payload(evidence)


def infer(
    evidence: dict[str, Any],
    *,
    params: dict[str, Any] | None = None,
    model_id: str = MODEL_ID,
    model_version: str = MODEL_VERSION,
    origen: Origen = Origen.SIMULADO,
) -> dict[str, Any]:
    """Inferencia determinista: misma entrada y mismos parámetros, mismo resultado."""
    if not model_version or not model_version.strip():
        raise MissingModelVersion("model_version es obligatorio")

    params = params or {}
    input_hash = evidence_input_hash(evidence)

    # Derivación determinista a partir de la huella de la entrada y del umbral.
    umbral = int(params.get("umbral", 0))
    bucket = (input_hash[0] + umbral) % len(LABELS)
    label = LABELS[bucket]
    confidence = Decimal(input_hash[1]) / Decimal(255) 
    confidence = confidence.quantize(Decimal("0.00001"))
    geometry = evidence.get("geometry")

    result_hash = detection_result_hash(
        input_hash=input_hash,
        model_id=model_id,
        model_version=model_version,
        params=params,
        label=label,
        confidence=confidence,
        geometry=geometry,
        origen=origen.value,
    )
    return {
        "model_id": model_id,
        "model_version": model_version,
        "label": label,
        "confidence": confidence,
        "geometry": geometry,
        "params": params,
        "input_hash": input_hash,
        "result_hash": result_hash,
        "origen": origen,
    }
