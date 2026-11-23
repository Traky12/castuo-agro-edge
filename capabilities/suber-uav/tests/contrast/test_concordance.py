"""Métricas de concordancia, contra valores conocidos.

Se comprueban contra resultados que se pueden verificar a mano: sin eso, una implementación
propia de una fórmula estadística es una fuente silenciosa de error.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from castuo.contrast.concordance import (
    METRIC_VERSION, OrdersDoNotMatch, kendall_tau_b, spearman,
)

BASE = {"a": 1, "b": 2, "c": 3, "d": 4}


def test_identical_orders_give_perfect_concordance():
    assert spearman(BASE, dict(BASE)) == Decimal("1")
    assert kendall_tau_b(BASE, dict(BASE)) == Decimal("1")


def test_reversed_orders_give_perfect_discordance():
    inverso = {"a": 4, "b": 3, "c": 2, "d": 1}
    assert spearman(BASE, inverso) == Decimal("-1")
    assert kendall_tau_b(BASE, inverso) == Decimal("-1")


def test_one_adjacent_swap_matches_the_hand_computed_value():
    """Con n=4 y un solo intercambio adyacente: Spearman 0,8 y Kendall 2/3."""
    swap = {"a": 1, "b": 2, "c": 4, "d": 3}
    assert spearman(BASE, swap) == Decimal("0.8")
    assert kendall_tau_b(BASE, swap) == Decimal("0.666667")


def test_ties_are_allowed_because_an_expert_may_not_want_to_break_them():
    con_empate = {"a": 1, "b": 1, "c": 3}
    sin_empate = {"a": 1, "b": 2, "c": 3}
    assert Decimal("0") < spearman(con_empate, sin_empate) < Decimal("1")
    assert Decimal("0") < kendall_tau_b(con_empate, sin_empate) < Decimal("1")


def test_orders_over_different_units_are_rejected():
    with pytest.raises(OrdersDoNotMatch, match="difieren"):
        spearman({"a": 1, "b": 2}, {"a": 1, "c": 2})


def test_a_single_unit_cannot_be_contrasted():
    with pytest.raises(OrdersDoNotMatch, match="al menos dos"):
        spearman({"a": 1}, {"a": 1})


def test_an_order_without_variation_is_rejected_instead_of_returning_zero():
    """Todos empatados no es concordancia nula: es ausencia de información, y devolver 0
    la haría pasar por un resultado."""
    plano = {"a": 1, "b": 1, "c": 1}
    with pytest.raises(OrdersDoNotMatch, match="sin variación"):
        spearman(plano, {"a": 1, "b": 2, "c": 3})


def test_the_metric_version_is_declared():
    """Va con cada resultado: un valor calculado hoy tiene que poder reproducirse aunque
    la implementación cambie."""
    assert METRIC_VERSION == "1.0.0"
