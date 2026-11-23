"""Canonicalización CASTUO-CANON-1.

El contrato está escrito en `docs/CANONICALIZACION.md`. Este módulo es una de sus dos
implementaciones; la otra vive dentro de `scripts/verify_package.py`, que no puede importar
este paquete porque una evidencia que solo verifica el software que la produjo no sirve
ante un tercero. Los vectores de `tests/fixtures/canonical_vectors.json` comprueban que
ambas emiten byte a byte lo mismo.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
import uuid as _uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

CANON_VERSION = 1

#: Valores generados que nunca entran en un contenido hasheado.
NON_DETERMINISTIC = frozenset({
    "detection_id", "asset_id", "review_id", "trace_id", "seal_id", "anchor_id",
    "proposal_id", "event_id",
    "detected_at", "created_at", "reviewed_at", "sealed_at", "anchored_at",
    "generated_at", "package_hash",
})


class NonCanonicalValue(ValueError):
    """El valor no tiene una representación canónica segura."""


def _decimal_text(value: Decimal) -> str:
    """Notación posicional normalizada: 0.90 -> 0.9, 1E+2 -> 100."""
    normalised = value.normalize()
    sign, digits, exponent = normalised.as_tuple()
    if isinstance(exponent, int) and exponent > 0:      # 1E+2 -> 100
        normalised = normalised.quantize(Decimal(1))
    return format(normalised, "f")


def _timestamp_text(value: datetime) -> str:
    if value.tzinfo is None:
        raise NonCanonicalValue(
            "un timestamp sin zona horaria no tiene interpretación única; usa UTC explícito"
        )
    utc = value.astimezone(timezone.utc).replace(microsecond=value.microsecond)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def normalise(value: Any) -> Any:
    """Lleva cualquier valor a la forma que la especificación fija."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        return _decimal_text(value)
    if isinstance(value, float):
        return _decimal_text(Decimal(str(value)))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    if isinstance(value, _uuid.UUID):
        return str(value).lower()
    if isinstance(value, datetime):
        return _timestamp_text(value)
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        items = ((unicodedata.normalize("NFC", str(k)), normalise(v)) for k, v in value.items())
        return {k: v for k, v in sorted(items, key=lambda kv: kv[0])}
    if isinstance(value, (list, tuple)):
        return [normalise(v) for v in value]
    if hasattr(value, "value") and type(value).__name__ == "Origen":
        return value.value
    raise NonCanonicalValue(f"tipo sin representación canónica: {type(value).__name__}")


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(normalise(payload), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(payload: Any) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_bytes(payload: Any) -> bytes:
    return hashlib.sha256(canonical_bytes(payload)).digest()


def strip_non_deterministic(payload: dict) -> dict:
    return {k: v for k, v in payload.items() if k not in NON_DETERMINISTIC}
