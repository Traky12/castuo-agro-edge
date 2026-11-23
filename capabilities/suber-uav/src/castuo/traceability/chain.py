"""Verificación de la cadena por dispositivo.

La cadena se particiona por dispositivo porque un orden total exigiría coordinación en
línea, y en campo no la hay (ADR-009). Cada dispositivo mantiene su propia secuencia; la
correlación entre dispositivos se establece después por sello, no por número de orden.
"""
from __future__ import annotations

from typing import Iterable, Sequence

from castuo.common.hashing import trace_event_hash
from castuo.traceability.events import TraceEvent


class BrokenChain(Exception):
    pass


def verify_chain(events: Sequence[TraceEvent]) -> None:
    """Comprueba que los eventos de UN dispositivo forman una cadena continua.

    Lanza `BrokenChain` con el motivo concreto: para un auditor, «la cadena falla en el
    evento 4 porque el hash anterior no coincide» es información; «cadena inválida» no.
    """
    if not events:
        return
    devices = {e.device_id for e in events}
    if len(devices) > 1:
        raise BrokenChain(f"la verificación es por dispositivo; recibidos {len(devices)}")

    ordered = sorted(events, key=lambda e: e.sequence_no)
    if ordered[0].sequence_no != 1:
        raise BrokenChain(f"la cadena no empieza en 1 (empieza en {ordered[0].sequence_no})")
    if ordered[0].previous_trace_hash is not None:
        raise BrokenChain("el primer evento no puede tener hash anterior")

    for prev, cur in zip(ordered, ordered[1:]):
        if cur.sequence_no != prev.sequence_no + 1:
            raise BrokenChain(
                f"hueco en la cadena: tras {prev.sequence_no} llega {cur.sequence_no}"
            )
        if cur.previous_trace_hash != prev.event_hash:
            raise BrokenChain(
                f"el evento {cur.sequence_no} no encadena con el {prev.sequence_no}"
            )

    # El hash de cada evento tiene que corresponder a su propio contenido: si solo se
    # comprobara el encadenado, se podría reescribir un evento y su hash a la vez.
    for e in ordered:
        recalculado = trace_event_hash(
            device_id=e.device_id, sequence_no=e.sequence_no, entity_type=e.entity_type,
            entity_id=e.entity_id, event_type=e.event_type, actor=e.actor,
            occurred_at=e.occurred_at, payload_hash=e.payload_hash,
            previous_trace_hash=e.previous_trace_hash,
            schema_version=e.schema_version, origen=e.origen.value,
        )
        if recalculado != e.event_hash:
            raise BrokenChain(
                f"el event_hash del evento {e.sequence_no} no corresponde a su contenido"
            )
