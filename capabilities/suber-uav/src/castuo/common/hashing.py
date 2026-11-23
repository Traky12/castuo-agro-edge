"""Hashes del dominio, construidos sobre la canonicalización CASTUO-CANON-1.

Este módulo no reimplementa nada: decide *qué* se hashea en cada caso. El *cómo* está en
`canonical.py` y en `docs/CANONICALIZACION.md`.
"""
from __future__ import annotations

from typing import Any

from castuo.common.canonical import (
    NON_DETERMINISTIC, canonical_bytes, sha256_bytes, sha256_hex,
)

__all__ = ["NON_DETERMINISTIC", "canonical_bytes", "sha256_bytes", "sha256_hex",
           "hash_payload", "detection_result_hash", "trace_event_hash"]


def hash_payload(payload: Any) -> bytes:
    return sha256_bytes(payload)


def detection_result_hash(*, input_hash: bytes, model_id: str, model_version: str,
                          params: dict, label: str, confidence: Any,
                          geometry: str | None, origen: str) -> bytes:
    """Cubre lo que determina el resultado y nada más.

    Si `detected_at` o el identificador generado entraran aquí, dos ejecuciones idénticas
    darían hashes distintos y la reproducibilidad sería imposible de afirmar.
    """
    return sha256_bytes({
        "input_hash": input_hash, "model_id": model_id, "model_version": model_version,
        "params": params, "label": label, "confidence": confidence,
        "geometry": geometry, "origen": origen,
    })


def trace_event_canonical(*, device_id, sequence_no: int, entity_type: str, entity_id,
                          event_type: str, actor, occurred_at, payload_hash: bytes,
                          previous_trace_hash: bytes | None, schema_version: int,
                          origen: str) -> dict:
    """Contenido completo del evento de traza.

    Incluye los metadatos —actor, tipo, entidad, origen, hora— además del payload: si la
    cadena encadenara solo `payload_hash`, se podría cambiar quién hizo qué sin romper la
    continuidad, que es exactamente lo que la cadena existe para impedir.
    """
    return {
        "device_id": device_id, "sequence_no": sequence_no, "entity_type": entity_type,
        "entity_id": entity_id, "event_type": event_type, "actor": actor,
        "occurred_at": occurred_at, "payload_hash": payload_hash,
        "previous_trace_hash": previous_trace_hash, "schema_version": schema_version,
        "origen": origen,
    }


def trace_event_hash(**campos) -> bytes:
    return sha256_bytes(trace_event_canonical(**campos))
