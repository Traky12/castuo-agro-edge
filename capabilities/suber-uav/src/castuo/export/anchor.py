"""Anclaje temporal RFC 3161.

Un token de sellado de tiempo **ancla** un hash existente: no modifica lo sellado. Lo que
hay que poder comprobar es que el `messageImprint` del token es el mismo `canonical_hash`
que guarda el sello; si no lo fuera, el token estaría certificando otra cosa.

Alcance honesto de este módulo: recorre la codificación DER buscando la estructura
`messageImprint` —AlgorithmIdentifier con el OID de SHA-256 seguido de un OCTET STRING de
32 bytes— sin construir un analizador CMS completo. Se ha probado contra tokens sintéticos
DER bien formados. **No se ha probado contra una autoridad de sellado real**, y esa prueba
es condición para usar esto fuera del entorno sintético. [PENDIENTE: token de TSA real]
"""
from __future__ import annotations

from enum import Enum

#: OID 2.16.840.1.101.3.4.2.1 (sha-256), codificado en DER.
OID_SHA256_DER = bytes.fromhex("0609608648016503040201")


class EstadoAnclaje(str, Enum):
    SELLO_LOCAL_SIN_ANCLAJE = "sello_local_sin_anclaje"
    ANCLAJE_VALIDO = "anclaje_valido"
    ANCLAJE_DE_OTRO_HASH = "anclaje_de_otro_hash"
    TOKEN_ILEGIBLE = "token_ilegible"


def extract_message_imprint(token: bytes) -> bytes | None:
    """Devuelve el hash SHA-256 anclado por el token, o None si no se localiza.

    Busca el patrón del `messageImprint`: el OID de SHA-256 (opcionalmente seguido de un
    NULL de parámetros) y a continuación un OCTET STRING de 32 bytes.
    """
    posicion = token.find(OID_SHA256_DER)
    while posicion != -1:
        cursor = posicion + len(OID_SHA256_DER)
        if token[cursor:cursor + 2] == b"\x05\x00":      # parámetros NULL, opcionales
            cursor += 2
        if token[cursor:cursor + 2] == b"\x04\x20":      # OCTET STRING de 32 bytes
            return token[cursor + 2:cursor + 34]
        posicion = token.find(OID_SHA256_DER, posicion + 1)
    return None


def verify_anchor(canonical_hash: bytes, token: bytes | None) -> EstadoAnclaje:
    """Contrato de cuatro estados, para que quien lea el resultado sepa qué tiene."""
    if token is None:
        return EstadoAnclaje.SELLO_LOCAL_SIN_ANCLAJE
    imprint = extract_message_imprint(token)
    if imprint is None:
        return EstadoAnclaje.TOKEN_ILEGIBLE
    if imprint != canonical_hash:
        return EstadoAnclaje.ANCLAJE_DE_OTRO_HASH
    return EstadoAnclaje.ANCLAJE_VALIDO


# ---------------------------------------------------------------- tokens sintéticos
def _der(tag: int, contenido: bytes) -> bytes:
    if len(contenido) < 0x80:
        return bytes([tag, len(contenido)]) + contenido
    longitud = len(contenido).to_bytes((len(contenido).bit_length() + 7) // 8, "big")
    return bytes([tag, 0x80 | len(longitud)]) + longitud + contenido


def synthetic_token(hash_anclado: bytes) -> bytes:
    """Token DER **sintético** con un messageImprint real.

    Sirve para ejercitar el verificador con una estructura DER de verdad en lugar de con
    una cadena inventada. No lleva firma ni cadena de confianza: no es un token válido de
    ninguna autoridad, y el paquete lo declara como `simulado`.
    """
    algoritmo = _der(0x30, OID_SHA256_DER + b"\x05\x00")
    message_imprint = _der(0x30, algoritmo + _der(0x04, hash_anclado))
    marca = _der(0x18, b"20260215091200Z")
    return _der(0x30, message_imprint + marca)
