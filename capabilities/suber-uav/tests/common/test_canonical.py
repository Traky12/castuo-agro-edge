"""Canonicalización: las dos implementaciones deben coincidir byte a byte.

La de la aplicación y la del verificador externo se escriben por separado a propósito —el
verificador no puede depender del software que produce la evidencia—, así que lo único que
garantiza que sigan de acuerdo es esta prueba sobre vectores fijos.
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import pathlib
import uuid
from decimal import Decimal

import pytest

from castuo.common.canonical import (
    CANON_VERSION, NonCanonicalValue, canonical_bytes, normalise, sha256_hex,
)

RAIZ = pathlib.Path(__file__).resolve().parents[2]
VECTORES = json.loads((RAIZ / "tests/fixtures/canonical_vectors.json").read_text(encoding="utf-8"))

# El verificador se carga por ruta, no por import: así la prueba comprueba justo lo que
# usará un tercero, un script suelto sin el paquete instalado.
_spec = importlib.util.spec_from_file_location("verificador", RAIZ / "scripts/verify_package.py")
verificador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verificador)


def rehidratar(valor):
    """Convierte los marcadores del fichero de vectores en objetos Python."""
    if isinstance(valor, str):
        if valor.startswith("DEC:"):   return Decimal(valor[4:])
        if valor.startswith("BYTES:"): return bytes.fromhex(valor[6:])
        if valor.startswith("UUID:"):  return uuid.UUID(valor[5:])
        if valor.startswith("TS:"):    return datetime.datetime.fromisoformat(valor[3:])
        return valor
    if isinstance(valor, dict):  return {k: rehidratar(v) for k, v in valor.items()}
    if isinstance(valor, list):  return [rehidratar(v) for v in valor]
    return valor


def test_vector_file_declares_the_supported_version():
    assert VECTORES["canon_version"] == CANON_VERSION


@pytest.mark.parametrize("vector", VECTORES["vectores"], ids=lambda v: v["nombre"])
def test_application_matches_the_frozen_vector(vector):
    """Si esto falla, la canonicalización ha cambiado: hay que subir `canon_version`."""
    valor = rehidratar(vector["entrada"])
    assert canonical_bytes(valor).decode("utf-8") == vector["canonico"]
    assert sha256_hex(valor) == vector["sha256"]


@pytest.mark.parametrize("vector", VECTORES["vectores"], ids=lambda v: v["nombre"])
def test_external_verifier_produces_the_same_bytes(vector):
    """El verificador recibe el valor ya normalizado, como viene dentro de un paquete."""
    normalizado = normalise(rehidratar(vector["entrada"]))
    assert verificador.canonical_bytes(normalizado).decode("utf-8") == vector["canonico"]
    assert verificador.sha256_hex(normalizado) == vector["sha256"]


def test_unicode_forms_collapse():
    """«árbol» precompuesto y con acento combinante son el mismo dato."""
    precompuesto = {"especie": "árbol"}
    combinante = {"especie": "árbol"}
    assert sha256_hex(precompuesto) == sha256_hex(combinante)


def test_timezones_collapse_to_utc():
    madrid = datetime.datetime(2026, 2, 15, 10, 12, tzinfo=datetime.timezone(
        datetime.timedelta(hours=1)))
    utc = datetime.datetime(2026, 2, 15, 9, 12, tzinfo=datetime.timezone.utc)
    assert sha256_hex({"t": madrid}) == sha256_hex({"t": utc})


def test_naive_timestamp_is_rejected():
    """Sin zona horaria no hay lectura única; fallar es más seguro que suponer UTC."""
    with pytest.raises(NonCanonicalValue, match="zona horaria"):
        canonical_bytes({"t": datetime.datetime(2026, 2, 15, 9, 12)})


def test_booleans_are_not_confused_with_integers():
    assert canonical_bytes({"v": True}) != canonical_bytes({"v": 1})
    assert canonical_bytes({"v": False}) != canonical_bytes({"v": 0})


def test_list_order_is_content():
    assert sha256_hex({"l": [1, 2]}) != sha256_hex({"l": [2, 1]})


def test_unknown_type_is_rejected_instead_of_silently_stringified():
    class Raro:  pass
    with pytest.raises(NonCanonicalValue):
        canonical_bytes({"x": Raro()})
