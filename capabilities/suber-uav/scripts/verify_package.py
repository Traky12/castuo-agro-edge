#!/usr/bin/env python3
"""Verificador externo de un paquete de evidencia CASTÚO.

Deliberadamente autónomo: no importa nada de `castuo` ni toca la base de datos. Si para
comprobar una evidencia hiciera falta el software que la produjo, no valdría ante un
tercero. Implementa el mismo contrato de canonicalización que la aplicación
(CASTUO-CANON-1, en docs/CANONICALIZACION.md); los vectores de
tests/fixtures/canonical_vectors.json comprueban que ambas emiten los mismos bytes.

Comprueba:
  1. hash del paquete
  2. hash canónico de la detección frente al sello
  3. correspondencia entre seal.subject_id y detection_id
  4. event_hash de cada evento de traza
  5. continuidad de la cadena por device_id
  6. sello local presente y bien formado
  7. anclaje RFC 3161, si existe
  8. origen de los datos

Uso:  python3 scripts/verify_package.py paquete.json [--json]
Sale con 0 si el paquete es íntegro, 1 si no. Un paquete íntegro pero simulado se avisa:
no es evidencia de campo.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from decimal import Decimal

CANON_VERSION_SOPORTADA = 1
OID_SHA256_DER = bytes.fromhex("0609608648016503040201")


# ------------------------------------------------------ CASTUO-CANON-1 (reimplementación)
def _decimal_text(value: Decimal) -> str:
    normalised = value.normalize()
    _, _, exponent = normalised.as_tuple()
    if isinstance(exponent, int) and exponent > 0:
        normalised = normalised.quantize(Decimal(1))
    return format(normalised, "f")


def normalise(value):
    """Mismas reglas que `castuo.common.canonical.normalise`.

    El paquete llega ya normalizado (todo son cadenas, enteros, listas y objetos), así que
    aquí solo quedan los casos que JSON puede devolver.
    """
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        return _decimal_text(Decimal(str(value)))
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        items = ((unicodedata.normalize("NFC", str(k)), normalise(v)) for k, v in value.items())
        return {k: v for k, v in sorted(items, key=lambda kv: kv[0])}
    if isinstance(value, (list, tuple)):
        return [normalise(v) for v in value]
    raise ValueError(f"tipo sin representación canónica: {type(value).__name__}")


def canonical_bytes(payload) -> bytes:
    return json.dumps(normalise(payload), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(payload) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


# ------------------------------------------------------------------ anclaje RFC 3161
def extract_message_imprint(token: bytes):
    posicion = token.find(OID_SHA256_DER)
    while posicion != -1:
        cursor = posicion + len(OID_SHA256_DER)
        if token[cursor:cursor + 2] == b"\x05\x00":
            cursor += 2
        if token[cursor:cursor + 2] == b"\x04\x20":
            return token[cursor + 2:cursor + 34]
        posicion = token.find(OID_SHA256_DER, posicion + 1)
    return None


# ------------------------------------------------------------------------ verificación
def verify(package: dict) -> tuple[list[str], list[str]]:
    """Devuelve (errores, avisos). Errores vacíos significa paquete íntegro."""
    errores: list[str] = []
    avisos: list[str] = []

    canon = package.get("canon_version")
    if canon != CANON_VERSION_SOPORTADA:
        errores.append(
            f"versión de canonicalización no soportada: {canon} "
            f"(este verificador implementa la {CANON_VERSION_SOPORTADA})")
        return errores, avisos      # sin el contrato correcto, el resto no significa nada

    # 1. hash del paquete
    contenido = {k: v for k, v in package.items() if k not in ("package_hash", "generated_at")}
    recalculado = sha256_hex(contenido)
    if recalculado != package.get("package_hash"):
        errores.append(f"el hash del paquete no cuadra: declarado "
                       f"{package.get('package_hash')}, recalculado {recalculado}")

    # 2 y 3. sello frente a la detección
    seal = package.get("seal") or {}
    detection = package.get("detection") or {}
    if not seal:
        errores.append("el paquete no incluye sello local")
    else:
        if seal.get("canonical_hash") != sha256_hex(detection):
            errores.append("el sello no corresponde al contenido de la detección incluida")
        if seal.get("subject_id") != package.get("detection_id"):
            errores.append("el sello apunta a otra detección")
        if seal.get("seal_kind") != "local":
            errores.append(f"tipo de sello inesperado: {seal.get('seal_kind')}")

    # 4 y 5. event_hash y continuidad por dispositivo
    por_dispositivo: dict[str, list[dict]] = {}
    for evento in package.get("trace", []):
        por_dispositivo.setdefault(evento["device_id"], []).append(evento)

    for dispositivo, eventos in por_dispositivo.items():
        eventos.sort(key=lambda e: e["sequence_no"])
        for evento in eventos:
            contenido_evento = {k: evento[k] for k in (
                "device_id", "sequence_no", "entity_type", "entity_id", "event_type",
                "actor", "occurred_at", "payload_hash", "previous_trace_hash",
                "schema_version", "origen") if k in evento}
            if sha256_hex(contenido_evento) != evento.get("event_hash"):
                errores.append(
                    f"el event_hash del evento {evento['sequence_no']} del dispositivo "
                    f"{dispositivo} no corresponde a su contenido")
        if eventos[0]["sequence_no"] != 1 or eventos[0].get("previous_trace_hash") is not None:
            errores.append(f"el dispositivo {dispositivo} no arranca correctamente la cadena")
        for anterior, actual in zip(eventos, eventos[1:]):
            if actual["sequence_no"] != anterior["sequence_no"] + 1:
                errores.append(f"hueco en la cadena del dispositivo {dispositivo}")
            if actual.get("previous_trace_hash") != anterior["event_hash"]:
                errores.append(f"el evento {actual['sequence_no']} del dispositivo "
                               f"{dispositivo} no encadena")

    # 7. anclaje certificado
    anclajes = package.get("seal_anchors") or []
    if not anclajes:
        avisos.append("sello local sin anclaje certificado: la hora la afirma el emisor, "
                      "no una autoridad independiente")
    for anclaje in anclajes:
        try:
            token = bytes.fromhex(anclaje.get("tsa_token", ""))
        except ValueError:
            errores.append("token de anclaje ilegible: no es hexadecimal")
            continue
        imprint = extract_message_imprint(token)
        if imprint is None:
            errores.append(f"token de {anclaje.get('authority')} ilegible: "
                           "no se localiza el messageImprint")
        elif imprint.hex() != seal.get("canonical_hash"):
            errores.append(f"el token de {anclaje.get('authority')} certifica otro hash")
        elif anclaje.get("origen") == "simulado":
            avisos.append(f"el anclaje de {anclaje.get('authority')} es simulado: "
                          "no procede de una autoridad de sellado real")

    # 8. origen
    origenes = {detection.get("origen")}
    if package.get("asset"):
        origenes.add(package["asset"].get("origen"))
    origenes |= {e.get("origen") for e in package.get("trace", [])}
    origenes.discard(None)
    if "simulado" in origenes:
        avisos.append("el paquete contiene datos SIMULADOS: es íntegro criptográficamente, "
                      "pero no constituye evidencia de campo")
    if len(origenes) > 1:
        avisos.append(f"el paquete mezcla orígenes: {sorted(origenes)}")

    return errores, avisos


def main() -> int:
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    como_json = "--json" in sys.argv
    if len(argumentos) != 1:
        print(__doc__)
        return 2

    with open(argumentos[0], encoding="utf-8") as fh:
        package = json.load(fh)

    errores, avisos = verify(package)

    if como_json:
        print(json.dumps({"integro": not errores, "errores": errores, "avisos": avisos},
                         ensure_ascii=False, indent=2))
    else:
        for aviso in avisos:
            print(f"AVISO: {aviso}")
        for error in errores:
            print(f"ERROR: {error}")
        print("PAQUETE NO VÁLIDO" if errores else "PAQUETE ÍNTEGRO")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
