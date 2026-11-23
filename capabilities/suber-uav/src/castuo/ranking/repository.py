"""Persistencia de protocolos, órdenes y concordancia.

El orden de las operaciones es el producto: protocolo → orden del sistema → sello → orden
del experto → concordancia. Ninguna de esas flechas se puede saltar, y el motor es quien lo
impide.
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal

from castuo.common.origen import SCHEMA_VERSION, Origen
from castuo.contrast.concordance import METRIC_VERSION, METRICAS


class ContrastRepository:
    def __init__(self, conn):
        self.conn = conn

    # ------------------------------------------------------------------ protocolo
    def register_protocol(self, *, scope_ref: str, unit_kind: str, metric: str,
                          threshold: Decimal, registered_by: uuid.UUID,
                          origen: Origen = Origen.SIMULADO) -> uuid.UUID:
        """El umbral se registra aquí, antes de que exista ningún dato.

        Es lo que impide elegir el listón después de ver el resultado: la concordancia lo
        copia de esta fila, no de quien la invoca.
        """
        protocol_id = uuid.uuid4()
        self.conn.execute(
            """INSERT INTO contrast_protocol (protocol_id, scope_ref, unit_kind, metric,
                        threshold, registered_by, schema_version, origen)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (protocol_id, scope_ref, unit_kind, metric, threshold, registered_by,
             SCHEMA_VERSION, origen.value))
        return protocol_id

    def protocol(self, protocol_id: uuid.UUID) -> dict:
        r = self.conn.execute(
            """SELECT protocol_id, scope_ref, unit_kind, metric, threshold, registered_by,
                      registered_at, schema_version, origen
               FROM contrast_protocol WHERE protocol_id = %s""", (protocol_id,)).fetchone()
        return {"protocol_id": r[0], "scope_ref": r[1], "unit_kind": r[2], "metric": r[3],
                "threshold": r[4], "registered_by": r[5], "registered_at": r[6],
                "schema_version": r[7], "origen": r[8]}

    # ------------------------------------------------------------------ orden del sistema
    def store_ranking(self, resultado: dict, *, protocol_id: uuid.UUID,
                      origen: Origen = Origen.SIMULADO) -> uuid.UUID:
        ranking_id = uuid.uuid4()
        self.conn.execute(
            """INSERT INTO ranking (ranking_id, protocol_id, model_id, model_version,
                        params, content_hash, schema_version, origen)
               VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s)""",
            (ranking_id, protocol_id, resultado["model_id"], resultado["model_version"],
             json.dumps(resultado["params"], sort_keys=True), resultado["content_hash"],
             SCHEMA_VERSION, origen.value))
        for item in resultado["items"]:
            self.conn.execute(
                """INSERT INTO ranking_item (ranking_item_id, ranking_id, unit_ref,
                            position, score, schema_version, origen)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (uuid.uuid4(), ranking_id, item["unit_ref"], item["position"],
                 item["score"], SCHEMA_VERSION, origen.value))
        return ranking_id

    def ranking(self, ranking_id: uuid.UUID) -> dict:
        r = self.conn.execute(
            """SELECT ranking_id, protocol_id, model_id, model_version, params,
                      content_hash, created_at, schema_version, origen
               FROM ranking WHERE ranking_id = %s""", (ranking_id,)).fetchone()
        items = self.conn.execute(
            """SELECT unit_ref, position, score FROM ranking_item
               WHERE ranking_id = %s ORDER BY position""", (ranking_id,)).fetchall()
        return {"ranking_id": r[0], "protocol_id": r[1], "model_id": r[2],
                "model_version": r[3], "params": r[4], "content_hash": bytes(r[5]),
                "created_at": r[6], "schema_version": r[7], "origen": r[8],
                "items": [{"unit_ref": i[0], "position": i[1], "score": i[2]} for i in items]}

    def positions(self, ranking_id: uuid.UUID) -> dict[str, int]:
        return {r[0]: r[1] for r in self.conn.execute(
            "SELECT unit_ref, position FROM ranking_item WHERE ranking_id = %s",
            (ranking_id,)).fetchall()}

    # ------------------------------------------------------------------ orden del experto
    def store_expert_ranking(self, *, ranking_id: uuid.UUID, actor: uuid.UUID,
                             orden: dict[str, int],
                             origen: Origen = Origen.SIMULADO) -> uuid.UUID:
        """El motor rechaza esta inserción si el orden del sistema no está sellado.

        La escritura va en su propio punto de guardado: un rechazo del muro es un
        resultado esperado del protocolo, no un accidente, y no debe arrastrar consigo el
        trabajo que el llamante ya hubiera hecho en la misma transacción.
        """
        expert_ranking_id = uuid.uuid4()
        with self.conn.transaction():      # SAVEPOINT si ya hay transacción abierta
            self.conn.execute(
                """INSERT INTO expert_ranking (expert_ranking_id, ranking_id, actor,
                            schema_version, origen) VALUES (%s,%s,%s,%s,%s)""",
                (expert_ranking_id, ranking_id, actor, SCHEMA_VERSION, origen.value))
            for unit_ref, position in sorted(orden.items(), key=lambda kv: kv[1]):
                self.conn.execute(
                    """INSERT INTO expert_ranking_item (expert_item_id, expert_ranking_id,
                                unit_ref, position, schema_version, origen)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (uuid.uuid4(), expert_ranking_id, unit_ref, position, SCHEMA_VERSION,
                     origen.value))
        return expert_ranking_id

    def expert_positions(self, expert_ranking_id: uuid.UUID) -> dict[str, int]:
        return {r[0]: r[1] for r in self.conn.execute(
            "SELECT unit_ref, position FROM expert_ranking_item WHERE expert_ranking_id = %s",
            (expert_ranking_id,)).fetchall()}

    # ------------------------------------------------------------------ concordancia
    def compute_concordance(self, *, ranking_id: uuid.UUID, expert_ranking_id: uuid.UUID,
                            origen: Origen = Origen.SIMULADO) -> dict:
        """Calcula y registra la concordancia.

        La métrica y el umbral se leen del protocolo: quien invoca esto no puede elegir
        ninguno de los dos, que es justo el punto.
        """
        protocol_id = self.conn.execute(
            "SELECT protocol_id FROM ranking WHERE ranking_id = %s", (ranking_id,)).fetchone()[0]
        protocolo = self.protocol(protocol_id)

        valor = METRICAS[protocolo["metric"]](
            self.positions(ranking_id), self.expert_positions(expert_ranking_id))
        veredicto = "supera" if valor >= protocolo["threshold"] else "no_supera"

        concordance_id = uuid.uuid4()
        self.conn.execute(
            """INSERT INTO concordance (concordance_id, ranking_id, expert_ranking_id,
                        metric, metric_version, value, threshold_applied, verdict,
                        schema_version, origen)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (concordance_id, ranking_id, expert_ranking_id, protocolo["metric"],
             METRIC_VERSION, valor, protocolo["threshold"], veredicto, SCHEMA_VERSION,
             origen.value))
        return {"concordance_id": concordance_id, "metric": protocolo["metric"],
                "metric_version": METRIC_VERSION, "value": valor,
                "threshold_applied": protocolo["threshold"], "verdict": veredicto}
