"""Regression tests for OC008 (Best-Buy buy/total/menu bugs)."""
import builtins

import pytest

import functions
import main
import products
import store


def _feed(monkeypatch, answers):
    """Replace input() with a scripted source; EOFError when exhausted."""
    it = iter(answers)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr(builtins, "input", fake_input)


def test_promoted_product_deactivates_at_zero():
    """Buying the last unit of a promoted product deactivates it."""
    from products_promotion import PercentageDiscount
    prod = products.Product("A", 10.0, 2)
    prod.set_promotion(PercentageDiscount(10))
    prod.buy(2)
    assert prod.quantity == 0
    assert prod.active is False


def test_limited_product_deactivates_at_zero():
    """Limited product deactivates when stock hits zero."""
    prod = products.LimitedProducts("L", 10.0, 2, 2)
    prod.buy(2)
    assert prod.active is False


def test_limited_product_rejects_more_than_stock():
    """Limited buy over stock raises ClassMethodException, not other."""
    prod = products.LimitedProducts("L", 10.0, 2, 2)
    with pytest.raises(products.ClassMethodException):
        prod.buy(5)
    assert prod.quantity == 2


@pytest.mark.parametrize("qty", [0, 601, -1])
def test_limited_product_invalid_quantity_raises(qty):
    """Invalid quantity raises instead of returning None."""
    prod = products.LimitedProducts("L", 10.0, 100, 2)
    with pytest.raises(products.ClassMethodException):
        prod.buy(qty)


def test_order_total_sums_all_items(monkeypatch, capsys):
    """Order TOTAL prints the sum, not the last item's price."""
    shop = store.Store([products.Product("A", 10.0, 10),
                        products.Product("B", 100.0, 10)])
    _feed(monkeypatch, ["1", "2", "2", "1", "x", "x"])
    main.make_an_order(shop)
    assert "TOTAL: 120" in capsys.readouterr().out


@pytest.mark.parametrize("idx", ["0", "9"])
def test_order_bad_index_no_crash(monkeypatch, capsys, idx):
    """Option 8 with out-of-range product number must not crash/wrap."""
    prod = products.Product("A", 10.0, 10)
    shop = store.Store([prod])
    _feed(monkeypatch, [idx, "1", "x", "x"])
    main.make_an_order(shop)
    assert prod.quantity == 10
    assert "Error" in capsys.readouterr().out


def test_order_limited_invalid_quantity_no_crash(monkeypatch):
    """Ordering amount 0 of a limited product must not TypeError."""
    shop = store.Store([products.LimitedProducts("L", 10.0, 100, 2)])
    _feed(monkeypatch, ["1", "0", "x", "x"])
    main.make_an_order(shop)


def test_total_amount_counts_all(capsys):
    """Option 2 total prints sum of quantities."""
    shop = store.Store([products.Product("A", 1.0, 3),
                        products.Product("B", 1.0, 4)])
    main.total_amount_in_store(shop)
    assert "7" in capsys.readouterr().out


def test_option9_empty_store_no_crash(monkeypatch, capsys):
    """Option 9 on an empty store reports empty instead of ValueError."""
    _feed(monkeypatch, [])
    functions.instance_logic_methods(store.Store([]))
    assert "empty" in capsys.readouterr().out.lower()


def test_compare_empty_store_no_crash(capsys):
    """Compare on empty store does not raise MinMaxRange."""
    out = functions.comparison_of_products(store.Store([]))
    assert "empty" in out.lower()


def test_main_loop_survives_eof(monkeypatch):
    """Closed stdin ends the menu cleanly instead of EOFError."""
    _feed(monkeypatch, [])
    main.opening_scene(store.Store([]))
