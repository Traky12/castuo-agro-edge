"""Paquete de exportación verificable.

Lleva dentro todo lo necesario para comprobarlo sin la aplicación ni la base de datos:
contenido de la detección, sello, anclajes, historial de estado y la cadena de eventos con
sus hashes. El número de versión de canonicalización viaja dentro para que un paquete
antiguo se siga verificando cuando el contrato evolucione.
"""
from __future__ import annotations

from datetime import datetime, timezone

from castuo.common.canonical import CANON_VERSION, normalise, sha256_hex
from castuo.export.seal import detection_canonical_payload

PACKAGE_VERSION = 2


def build_package(*, detection, asset, asset_status, status_history, proposals, reviews,
                  seal, anchors, trace_events) -> dict:
    """`generated_at` y `package_hash` quedan fuera del hash: no son contenido."""
    content = {
        "canon_version": CANON_VERSION,
        "package_version": PACKAGE_VERSION,
        "detection_id": str(detection.detection_id),
        "detection": normalise(detection_canonical_payload(detection)),
        "asset": normalise({
            "asset_id": asset.asset_id, "asset_type": asset.asset_type,
            "geometry": asset.geometry, "owner_ref": asset.owner_ref,
            "initial_status": asset.initial_status, "status": asset_status,
            "source_event_id": asset.source_event_id, "captured_at": asset.captured_at,
            "schema_version": asset.schema_version, "origen": asset.origen,
        }) if asset is not None else None,
        "asset_status_history": [
            normalise({"from_status": e.from_status, "to_status": e.to_status,
                       "actor": e.actor, "reason": e.reason, "origen": e.origen})
            for e in status_history
        ],
        "asset_proposals": [
            normalise({"detection_id": d, "asset_id": a, "origen": o})
            for d, a, o in proposals
        ],
        "reviews": [
            normalise({"review_id": r.review_id, "verdict": r.verdict,
                       "review_type": r.review_type, "actor": r.actor,
                       "seal_id": r.seal_id, "origen": r.origen})
            for r in reviews
        ],
        "seal": normalise({
            "seal_id": seal["seal_id"], "subject_type": seal["subject_type"],
            "subject_id": seal["subject_id"], "canonical_hash": seal["canonical_hash"],
            "seal_kind": seal["seal_kind"], "schema_version": seal["schema_version"],
            "origen": seal["origen"],
        }),
        "seal_anchors": [normalise(a) for a in anchors],
        "trace": [
            normalise({
                "device_id": e.device_id, "sequence_no": e.sequence_no,
                "entity_type": e.entity_type, "entity_id": e.entity_id,
                "event_type": e.event_type, "actor": e.actor,
                "occurred_at": e.occurred_at, "payload_hash": e.payload_hash,
                "event_hash": e.event_hash, "previous_trace_hash": e.previous_trace_hash,
                "schema_version": e.schema_version, "origen": e.origen,
            })
            for e in sorted(trace_events, key=lambda e: (str(e.device_id), e.sequence_no))
        ],
    }
    return {
        **content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_hash": sha256_hex(content),
    }


def package_content(package: dict) -> dict:
    return {k: v for k, v in package.items() if k not in ("package_hash", "generated_at")}
