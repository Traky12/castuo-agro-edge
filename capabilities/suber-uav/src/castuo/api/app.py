"""API HTTP del demostrador.

Cada operación que escribe deja su evento de traza en la cadena del dispositivo
autenticado: la API no es una capa de conveniencia sobre la base de datos, es el punto
donde se registra quién hizo qué. Las respuestas son deterministas —mismo estado y misma
petición, misma respuesta— para que un cliente sin conexión pueda reintentar sin miedo.

Fuera de alcance en este incremento: aplicación móvil, sincronización real, panel de
administración, integración productiva del dron.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from castuo.api.auth import CABECERA, Dispositivo, autenticar
from castuo.common.origen import Origen
from castuo.detection import service as deteccion_service
from castuo.detection.repository import DetectionRepository
from castuo.export.package import build_package
from castuo.export.seal import SealRepository
from castuo.inventory.repository import InventoryRepository
from castuo.inventory.status import AssetStatusRepository
from castuo.ranking import service as ranking_service
from castuo.ranking.repository import ContrastRepository
from castuo.review.models import ReviewRepository
from castuo.storage.connection import connect_owner
from castuo.traceability import events as ev
from castuo.traceability.repository import TraceRepository

app = FastAPI(title="CASTÚO-CORCHO · demostrador", version="0.2.0",
              description="Núcleo de evidencia. Todos los datos de este entorno son "
                          "sintéticos y viajan marcados como tales.")


def conexion(request: Request):
    """Una conexión por petición, con transacción explícita.

    La fábrica es sustituible para que las pruebas usen la suya sin levantar un servidor
    contra otra base de datos.
    """
    fabrica = getattr(app.state, "conn_factory", connect_owner)
    conn = fabrica()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if getattr(app.state, "close_conn", True):
            conn.close()


def dispositivo(conn=Depends(conexion),
                clave: Annotated[str | None, Header(alias=CABECERA)] = None) -> Dispositivo:
    d = autenticar(conn, clave)
    if d is None:
        # Mismo mensaje para clave ausente, inválida o revocada: distinguirlos regala
        # información a quien esté probando claves.
        raise HTTPException(status_code=401, detail="credencial no válida")
    return d


# --------------------------------------------------------------------------- contratos
class EvidenciaIn(BaseModel):
    source_event_id: str = Field(min_length=1, max_length=200)
    asset_type: str
    geometry: str | None = None
    origen: str = "simulado"


class DeteccionIn(BaseModel):
    evidence_id: str = Field(min_length=1)
    evidence: dict[str, Any]
    params: dict[str, Any] = Field(default_factory=dict)
    origen: str = "simulado"


class ProtocoloIn(BaseModel):
    scope_ref: str
    unit_kind: str
    metric: str
    threshold: Decimal = Field(ge=-1, le=1)


class RankingIn(BaseModel):
    protocol_id: uuid.UUID
    unidades: list[dict[str, Any]] = Field(min_length=2)
    params: dict[str, Any] = Field(default_factory=dict)


class OrdenExpertoIn(BaseModel):
    orden: dict[str, int] = Field(min_length=2)


# --------------------------------------------------------------------------- endpoints
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "entorno": "sintetico"}


@app.post("/v1/evidence", status_code=201)
def ingerir_evidencia(cuerpo: EvidenciaIn, conn=Depends(conexion),
                      d: Dispositivo = Depends(dispositivo)) -> dict:
    """Alta de activo, idempotente por `source_event_id`.

    Reenviar el mismo evento devuelve 200 y el mismo identificador en lugar de 201: un
    cliente que reintenta tras un corte de red no crea duplicados ni recibe un error.
    """
    inventario = InventoryRepository(conn)
    activo, creado = inventario.ingest_asset(
        source_event_id=cuerpo.source_event_id, asset_type=cuerpo.asset_type,
        geometry=cuerpo.geometry, origen=Origen(cuerpo.origen))

    if creado:
        TraceRepository(conn).append(
            device_id=d.device_id, entity_type="asset", entity_id=activo.asset_id,
            event_type=ev.ASSET_INGESTED, actor=d.device_id,
            payload={"source_event_id": cuerpo.source_event_id})

    return {"asset_id": str(activo.asset_id), "creado": creado,
            "status": inventario.current_status(activo.asset_id),
            "origen": activo.origen.value}


@app.post("/v1/detections", status_code=201)
def crear_deteccion(cuerpo: DeteccionIn, conn=Depends(conexion),
                    d: Dispositivo = Depends(dispositivo)) -> dict:
    resultado = deteccion_service.infer(
        cuerpo.evidence, params=cuerpo.params, origen=Origen(cuerpo.origen))
    deteccion = DetectionRepository(conn).add(resultado, evidence_id=cuerpo.evidence_id)

    TraceRepository(conn).append(
        device_id=d.device_id, entity_type="detection", entity_id=deteccion.detection_id,
        event_type=ev.DETECTION_CREATED, actor=d.device_id,
        payload={"result_hash": deteccion.result_hash.hex()})

    return {"detection_id": str(deteccion.detection_id), "label": deteccion.label,
            "confidence": str(deteccion.confidence),
            "model_version": deteccion.model_version,
            "result_hash": deteccion.result_hash.hex(), "origen": deteccion.origen.value}


@app.post("/v1/protocols", status_code=201)
def registrar_protocolo(cuerpo: ProtocoloIn, conn=Depends(conexion),
                        d: Dispositivo = Depends(dispositivo)) -> dict:
    """El umbral se fija aquí, antes de que exista ningún orden ni ningún dato."""
    protocol_id = ContrastRepository(conn).register_protocol(
        scope_ref=cuerpo.scope_ref, unit_kind=cuerpo.unit_kind, metric=cuerpo.metric,
        threshold=cuerpo.threshold, registered_by=d.device_id)
    return {"protocol_id": str(protocol_id), "threshold": str(cuerpo.threshold),
            "metric": cuerpo.metric}


@app.post("/v1/rankings", status_code=201)
def crear_ranking(cuerpo: RankingIn, conn=Depends(conexion),
                  d: Dispositivo = Depends(dispositivo)) -> dict:
    repo = ContrastRepository(conn)
    try:
        resultado = ranking_service.rank(cuerpo.unidades, params=cuerpo.params)
    except ranking_service.DescriptoresInvalidos as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    ranking_id = repo.store_ranking(resultado, protocol_id=cuerpo.protocol_id)
    TraceRepository(conn).append(
        device_id=d.device_id, entity_type="ranking", entity_id=ranking_id,
        event_type="ranking.created", actor=d.device_id,
        payload={"content_hash": resultado["content_hash"].hex()})

    return {"ranking_id": str(ranking_id),
            "content_hash": resultado["content_hash"].hex(),
            "model_version": resultado["model_version"],
            "orden": [{"unit_ref": i["unit_ref"], "position": i["position"],
                       "score": str(i["score"])} for i in resultado["items"]]}


@app.post("/v1/rankings/{ranking_id}/seal", status_code=201)
def sellar_ranking(ranking_id: uuid.UUID, conn=Depends(conexion),
                   d: Dispositivo = Depends(dispositivo)) -> dict:
    """Congela el orden. A partir de aquí puede entrar el del experto, y no antes."""
    repo = ContrastRepository(conn)
    datos = repo.ranking(ranking_id)
    from castuo.common.origen import SCHEMA_VERSION
    seal_id = uuid.uuid4()
    conn.execute(
        """INSERT INTO seal (seal_id, subject_type, subject_id, canonical_hash,
                    seal_kind, schema_version, origen)
           VALUES (%s,'ranking',%s,%s,'local',%s,%s)""",
        (seal_id, ranking_id, datos["content_hash"], SCHEMA_VERSION, datos["origen"]))
    TraceRepository(conn).append(
        device_id=d.device_id, entity_type="seal", entity_id=seal_id,
        event_type=ev.SEAL_CREATED, actor=d.device_id, payload={"ranking_id": str(ranking_id)})
    return {"seal_id": str(seal_id), "canonical_hash": datos["content_hash"].hex(),
            "seal_kind": "local", "anclaje_certificado": None}


@app.post("/v1/rankings/{ranking_id}/expert-order", status_code=201)
def cargar_orden_experto(ranking_id: uuid.UUID, cuerpo: OrdenExpertoIn,
                         conn=Depends(conexion),
                         d: Dispositivo = Depends(dispositivo)) -> dict:
    import psycopg
    repo = ContrastRepository(conn)
    try:
        experto = repo.store_expert_ranking(
            ranking_id=ranking_id, actor=d.device_id, orden=cuerpo.orden)
    except psycopg.errors.RestrictViolation as exc:
        # El muro: el motor rechaza cargar el orden experto sin sello previo.
        raise HTTPException(status_code=409, detail=str(exc).split("\n")[0])
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409,
                            detail="este actor ya cargó un orden para este ranking")
    return {"expert_ranking_id": str(experto)}


@app.post("/v1/rankings/{ranking_id}/concordance", status_code=201)
def calcular_concordancia(ranking_id: uuid.UUID, expert_ranking_id: uuid.UUID,
                          conn=Depends(conexion),
                          d: Dispositivo = Depends(dispositivo)) -> dict:
    from castuo.contrast.concordance import OrdersDoNotMatch
    repo = ContrastRepository(conn)
    try:
        resultado = repo.compute_concordance(
            ranking_id=ranking_id, expert_ranking_id=expert_ranking_id)
    except OrdersDoNotMatch as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {k: (str(v) if isinstance(v, (Decimal, uuid.UUID)) else v)
            for k, v in resultado.items()}


@app.get("/v1/rankings/{ranking_id}")
def leer_ranking(ranking_id: uuid.UUID, conn=Depends(conexion),
                 d: Dispositivo = Depends(dispositivo)) -> dict:
    datos = ContrastRepository(conn).ranking(ranking_id)
    sello = conn.execute(
        "SELECT seal_id, sealed_at FROM seal WHERE subject_type='ranking' AND subject_id=%s",
        (ranking_id,)).fetchone()
    return {"ranking_id": str(ranking_id), "model_version": datos["model_version"],
            "content_hash": datos["content_hash"].hex(), "origen": datos["origen"],
            "sellado": sello is not None,
            "orden": [{"unit_ref": i["unit_ref"], "position": i["position"],
                       "score": str(i["score"])} for i in datos["items"]]}


@app.post("/v1/verify")
def verificar(paquete: dict, conn=Depends(conexion),
              d: Dispositivo = Depends(dispositivo)) -> dict:
    """Verificador como servicio.

    Carga el script externo por ruta en lugar de importar la lógica: así el servicio ejecuta
    exactamente el mismo código que ejecutaría un tercero por su cuenta, y no una variante
    que podría divergir sin que nadie lo note.
    """
    import importlib.util
    import pathlib
    ruta = pathlib.Path(__file__).resolve().parents[3] / "scripts/verify_package.py"
    spec = importlib.util.spec_from_file_location("verificador_externo", ruta)
    verificador = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verificador)

    errores, avisos = verificador.verify(paquete)
    return {"integro": not errores, "errores": errores, "avisos": avisos}
