"""Procedencia del dato. Obligatorio e inmutable en toda entidad (ADR-011).

Existe como enum en Python y como tipo en PostgreSQL: si un dato simulado pudiera
pasar por real en algún punto, contaminaría todo lo que se construya encima.
"""
from enum import Enum


class Origen(str, Enum):
    REAL = "real"
    SIMULADO = "simulado"
    HISTORICO = "historico"


SCHEMA_VERSION = 1
