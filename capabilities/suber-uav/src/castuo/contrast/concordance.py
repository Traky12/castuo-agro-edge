"""Medidas de concordancia ordinal.

Sin dependencias externas a propósito: son cuarenta líneas, y una dependencia científica
para esto obligaría a fijar su versión dentro del contrato de reproducibilidad. La versión
del método viaja con cada resultado (`METRIC_VERSION`) para que un valor calculado hoy se
pueda reproducir mañana aunque la implementación cambie.

Las dos métricas admiten empates, porque un corchero puede considerar dos rodales
igual de prioritarios y forzarle a desempatar sería inventar información.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Sequence

METRIC_VERSION = "1.0.0"


class OrdersDoNotMatch(ValueError):
    """Los dos órdenes no cubren exactamente las mismas unidades."""


def _rangos(posiciones: Sequence[float]) -> list[float]:
    """Rangos con media en los empates, que es lo que exigen Spearman y Kendall tau-b."""
    ordenados = sorted(range(len(posiciones)), key=lambda i: posiciones[i])
    rangos = [0.0] * len(posiciones)
    i = 0
    while i < len(ordenados):
        j = i
        while j + 1 < len(ordenados) and posiciones[ordenados[j + 1]] == posiciones[ordenados[i]]:
            j += 1
        medio = (i + j) / 2 + 1
        for k in range(i, j + 1):
            rangos[ordenados[k]] = medio
        i = j + 1
    return rangos


def _alinear(sistema: dict[str, int], experto: dict[str, int]) -> tuple[list[float], list[float]]:
    if set(sistema) != set(experto):
        faltan = set(sistema) ^ set(experto)
        raise OrdersDoNotMatch(
            f"los dos órdenes deben cubrir las mismas unidades; difieren en {sorted(faltan)}")
    if len(sistema) < 2:
        raise OrdersDoNotMatch("hacen falta al menos dos unidades para medir concordancia")
    unidades = sorted(sistema)
    return ([float(sistema[u]) for u in unidades], [float(experto[u]) for u in unidades])


def spearman(sistema: dict[str, int], experto: dict[str, int]) -> Decimal:
    """Rho de Spearman sobre rangos, con corrección por empates."""
    a, b = _alinear(sistema, experto)
    ra, rb = _rangos(a), _rangos(b)
    n = len(ra)
    media_a = sum(ra) / n
    media_b = sum(rb) / n
    cov = sum((x - media_a) * (y - media_b) for x, y in zip(ra, rb))
    var_a = sum((x - media_a) ** 2 for x in ra)
    var_b = sum((y - media_b) ** 2 for y in rb)
    if var_a == 0 or var_b == 0:
        raise OrdersDoNotMatch("un orden sin variación no permite medir concordancia")
    return Decimal(str(cov / (var_a * var_b) ** 0.5)).quantize(Decimal("0.000001"))


def kendall_tau_b(sistema: dict[str, int], experto: dict[str, int]) -> Decimal:
    """Tau-b de Kendall: proporción de pares ordenados igual, corregida por empates."""
    a, b = _alinear(sistema, experto)
    n = len(a)
    concordantes = discordantes = empates_a = empates_b = 0
    for i in range(n):
        for j in range(i + 1, n):
            da, db = a[i] - a[j], b[i] - b[j]
            if da == 0 and db == 0:
                empates_a += 1
                empates_b += 1
            elif da == 0:
                empates_a += 1
            elif db == 0:
                empates_b += 1
            elif (da > 0) == (db > 0):
                concordantes += 1
            else:
                discordantes += 1
    total = n * (n - 1) / 2
    denominador = ((total - empates_a) * (total - empates_b)) ** 0.5
    if denominador == 0:
        raise OrdersDoNotMatch("un orden sin variación no permite medir concordancia")
    return Decimal(str((concordantes - discordantes) / denominador)).quantize(Decimal("0.000001"))


METRICAS = {"spearman": spearman, "kendall_tau_b": kendall_tau_b}
