"""Reidentificación entre misiones — la métrica del gate G1.

G1 pregunta una sola cosa: ¿se puede volver a encontrar el mismo pie en dos vuelos
distintos? Sin eso no hay serie temporal, y sin serie temporal el resto del sistema es un
inventario caro.

Método, declarado antes de mirar ningún dato:

- Se emparejan observaciones por **vecino mutuo más cercano** dentro de una tolerancia
  pactada de antemano. Mutuo, y no «el más cercano de A en B», porque el segundo criterio
  no es simétrico: invirtiendo las misiones daría otro resultado, y una métrica que depende
  del orden en que se pasan los argumentos no vale para un gate.
- Los empates se rompen por `unit_ref` ascendente, de modo que el resultado es determinista.
- La distancia es euclídea sobre las coordenadas del WKT. **No es distancia geodésica**: es
  válida si las coordenadas están proyectadas en metros, y engañosa si están en grados. La
  proyección es una decisión pendiente. `[POR DECIDIR EN F0: sistema de referencia]`

La tolerancia NO tiene valor por defecto. Se pasa siempre de forma explícita, y en el gate
se registra antes de mirar los datos, por la misma razón que el umbral de concordancia
(ADR-022): fijarla después es elegir el listón que uno acaba de saltar.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

METRIC_VERSION = "1.0.0"

_PUNTO = re.compile(r"^\s*POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)\s*$",
                    re.IGNORECASE)


class GeometriaNoSoportada(ValueError):
    """La reidentificación solo entiende POINT; cualquier otra geometría se rechaza."""


def punto(wkt: str | None) -> tuple[float, float]:
    if wkt is None:
        raise GeometriaNoSoportada("una observación sin geometría no se puede reidentificar")
    m = _PUNTO.match(wkt)
    if not m:
        raise GeometriaNoSoportada(f"se esperaba POINT(x y) y llegó: {wkt!r}")
    return float(m.group(1)), float(m.group(2))


def distancia(a: str | None, b: str | None) -> float:
    (ax, ay), (bx, by) = punto(a), punto(b)
    return math.hypot(ax - bx, ay - by)


@dataclass(frozen=True)
class Emparejamiento:
    unit_a: str
    unit_b: str
    distancia_m: float


@dataclass(frozen=True)
class Reidentificacion:
    """Resultado del contraste entre dos misiones sobre el mismo rodal."""
    metric_version: str
    tolerancia_m: float
    total_a: int
    total_b: int
    emparejadas: tuple[Emparejamiento, ...]
    solo_en_a: tuple[str, ...]
    solo_en_b: tuple[str, ...]

    @property
    def tasa_reencuentro(self) -> float:
        """Proporción de pies de la primera misión reencontrados en la segunda."""
        if self.total_a == 0:
            return 0.0
        return len(self.emparejadas) / self.total_a

    @property
    def jaccard(self) -> float:
        """Solape entre ambos conjuntos. Penaliza tanto perder pies como inventarlos."""
        union = self.total_a + self.total_b - len(self.emparejadas)
        if union == 0:
            return 0.0
        return len(self.emparejadas) / union

    @property
    def desviacion_media_m(self) -> float:
        if not self.emparejadas:
            return 0.0
        return sum(e.distancia_m for e in self.emparejadas) / len(self.emparejadas)


def _clave(obs) -> str:
    return obs.unit_ref


def reidentificar(observaciones_a, observaciones_b, *, tolerancia_m: float) -> Reidentificacion:
    """Empareja por vecino mutuo más cercano dentro de `tolerancia_m`.

    `observaciones_a` y `observaciones_b` son iterables de objetos con `unit_ref` y
    `geometry`. La tolerancia es obligatoria y debe ser positiva.
    """
    if tolerancia_m <= 0:
        raise ValueError("la tolerancia debe ser positiva y pactarse antes de mirar el dato")

    a = sorted(observaciones_a, key=_clave)
    b = sorted(observaciones_b, key=_clave)

    # Candidatos dentro de tolerancia, ordenados por distancia y después por unit_ref para
    # que un empate exacto de distancias no dependa del orden de llegada.
    candidatos: list[tuple[float, str, str]] = []
    for oa in a:
        for ob in b:
            d = distancia(oa.geometry, ob.geometry)
            if d <= tolerancia_m:
                candidatos.append((d, oa.unit_ref, ob.unit_ref))
    candidatos.sort()

    usados_a: set[str] = set()
    usados_b: set[str] = set()
    emparejadas: list[Emparejamiento] = []
    for d, ua, ub in candidatos:
        if ua in usados_a or ub in usados_b:
            continue
        usados_a.add(ua)
        usados_b.add(ub)
        emparejadas.append(Emparejamiento(unit_a=ua, unit_b=ub, distancia_m=d))

    emparejadas.sort(key=lambda e: e.unit_a)
    return Reidentificacion(
        metric_version=METRIC_VERSION,
        tolerancia_m=float(tolerancia_m),
        total_a=len(a),
        total_b=len(b),
        emparejadas=tuple(emparejadas),
        solo_en_a=tuple(o.unit_ref for o in a if o.unit_ref not in usados_a),
        solo_en_b=tuple(o.unit_ref for o in b if o.unit_ref not in usados_b),
    )
