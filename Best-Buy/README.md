# Best-Buy

A command-line store inventory and ordering program written in Python.

Status: learning exercise. Not production software.

## What it does

The program starts with a hard-coded in-memory inventory (six products) and shows a text menu. You can list, add and remove products, attach promotions to them, look products up by name, compare prices and place an order. Nothing is saved: all data is lost when the program exits.

## Run it

Requires Python 3 and, on a clean machine, the `requests` package (see Known limitations). From the `Best-Buy` folder, in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install requests
python main.py
```

## Menu

```text
1. List all products in store
2. Show total amount in store
3. Add new product in store
4. Remove a product in store
5. Add promotion
6. Remove promotion
7. Show product details
8. Make an order
9. Comperasion of  products
10. Quit
```

The labels, including the spelling of option 9, are copied from `main.py`. Option 8 asks for pairs of "product number" and "amount"; entering anything non-numeric ends the order.

## Classes

All constructor signatures are taken from the code.

- `Product(name, price, quantity)` in `products.py`: base class. Names are title-cased, quantity cannot be negative, and `buy(quantity)` returns the price and lowers the stock. Invalid input raises `ClassMethodException`.
- `QuantitativelessProducts(name, price)`: a product with a fixed quantity of 1 (the default inventory uses it for a software licence). It can only be bought with quantity 1 and cannot be deactivated.
- `LimitedProducts(name, price, quantity, count)`: `count` is the number of orders allowed (`allowed_ship_count`); it cannot exceed `quantity`.
- `Store(product_list)` in `store.py`: holds the stock list. Methods: `add_product`, `remove_product`, `get_total_quantity`, `get_all_products` (active products only). Errors raise `StoreExceptions`. `Store` has no order method; ordering is the function `make_an_order` in `main.py`.
- Promotions in `products_promotion.py`, all subclasses of the abstract `Promation` and exposing `apply_promotion(price, quantity)`:
  - `PercentageDiscount(discount_ratio)`: ratio is a percentage.
  - `SecondHalfPrice(steps)`: the menu passes `steps=2`.
  - `ThirdOneFree(steps)`: the menu passes `steps=3`.

`functions.py` holds the menu helpers for promotions, product details, order input and the price comparison. `ioput.py` holds the validated input helpers (`read_int_ranged`, `read_float`, `ask_to_continue` and similar).

## Tests

Run from the `Best-Buy` folder:

```powershell
python -m unittest unittest_products unittest_store product_unittest
```

This runs 20 tests, which pass on a copy of the folder. Plain `python -m unittest discover` finds 0 tests because the test files do not follow the `test*.py` naming pattern.

## Project structure

```text
Best-Buy/
  main.py                menu loop, default inventory, order flow
  products.py            Product, QuantitativelessProducts, LimitedProducts
  products_promotion.py  Promation (abstract), PercentageDiscount, SecondHalfPrice, ThirdOneFree
  store.py               Store
  functions.py           promotion, details, order input and comparison helpers
  ioput.py               input validation helpers
  unittest_products.py   tests
  unittest_store.py      tests
  product_unittest.py    tests
  requirements.txt       comments only, no packages listed (its comment that no external dependencies are needed is wrong, see Known limitations)
```

## Known limitations

- `ioput.py` imports `requests` for `page_request`, which nothing calls. `requirements.txt` lists no packages, so a clean machine needs `pip install requests` or `main.py` fails on import.
- `Product.buy` only sets `active = False` on the non-promotion path (`products.py`), and `LimitedProducts.buy` never does. Listings are unaffected, because `Store.get_all_products` filters on `quantity > 0`, not on the `active` flag.
- Option 8 prints the cost of the last successfully bought item as the order total (`main.py`, `ORDER MADE, TOTAL`), not the sum of the whole order.
- Option 8 crashes with a traceback in two cases: a product number outside the list raises `IndexError` (`main.py`), and ordering more than a `LimitedProducts` item allows raises `TypeError`, because `LimitedProducts.buy` returns `None` when the quantity check fails.
- Option 9 calls `max()` and `min()` on the stock, so it raises `ValueError` once every product has been removed, and it includes inactive products.
- Closed or piped input ends the program with an `EOFError` traceback (`ioput.py`).
- `store.py` contains a helper named `test_remove_product` that builds a sample store and is not a real test.
- The comparison submenu (option 9) is price-only: max, min, two sorted lists and a two-product price comparison.
- Data is in memory only and the default inventory is hard-coded in `main.py`.

## License

MIT, see [LICENSE](../LICENSE).
