"""Autenticación de dispositivos.

La clave llega en la cabecera y se compara por su hash: la base de datos nunca guarda la
credencial en claro, de modo que una filtración del volcado no entrega accesos. El
dispositivo autenticado es además quien firma la cadena de traza, así que la autenticación
no es solo un control de acceso: determina en qué cadena se escribe.

Provisional por diseño. Falta rotación, caducidad y revocación auditada antes de que esto
salga de un entorno de pruebas. [PENDIENTE: esquema de credenciales de producción]
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass

from castuo.common.origen import SCHEMA_VERSION, Origen

CABECERA = "X-CASTUO-Key"


@dataclass(frozen=True)
class Dispositivo:
    device_id: uuid.UUID
    label: str


def hash_clave(clave: str) -> bytes:
    return hashlib.sha256(clave.encode("utf-8")).digest()


def enrolar(conn, *, label: str, origen: Origen = Origen.SIMULADO) -> tuple[uuid.UUID, str]:
    """Da de alta un dispositivo y devuelve su clave UNA sola vez.

    No se puede recuperar después: solo se guarda el hash. Si se pierde, se revoca el
    dispositivo y se enrola otro, que es también lo que se querría en campo.
    """
    device_id = uuid.uuid4()
    clave = secrets.token_urlsafe(32)
    conn.execute(
        """INSERT INTO device (device_id, label, api_key_hash, schema_version, origen)
           VALUES (%s,%s,%s,%s,%s)""",
        (device_id, label, hash_clave(clave), SCHEMA_VERSION, origen.value))
    return device_id, clave


def autenticar(conn, clave: str | None) -> Dispositivo | None:
    """Devuelve el dispositivo activo asociado a la clave, o None."""
    if not clave:
        return None
    fila = conn.execute(
        """SELECT device_id, label FROM device
           WHERE api_key_hash = %s AND revoked_at IS NULL""",
        (hash_clave(clave),)).fetchone()
    return Dispositivo(fila[0], fila[1]) if fila else None


def revocar(conn, device_id: uuid.UUID) -> None:
    conn.execute("UPDATE device SET revoked_at = now() WHERE device_id = %s", (device_id,))
