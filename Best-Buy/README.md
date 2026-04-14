# Best-Buy Store Management System

Command-line inventory management system demonstrating object-oriented programming with Python.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![unittest](https://img.shields.io/badge/Testing-unittest-green.svg)

---

## Overview

Python CLI application simulating a complete e-commerce inventory management system. Built using OOP principles with class inheritance, polymorphism, and comprehensive error handling for managing different product types and promotional systems.

---

## Features

- **Multiple Product Types**: Regular, quantityless (licenses), and limited purchase products
- **Promotion System**: Percentage discounts, second-item promotions, and buy-X-get-Y deals
- **Inventory Management**: Add/remove products, update quantities, check stock levels
- **Order Processing**: Shopping cart with automatic price calculation and promotion application
- **Product Comparison**: Compare prices and attributes between products
- **Validation**: Input validation with custom exceptions for business logic
- **Unit Testing**: Comprehensive test coverage for products and store operations

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Core programming language |
| unittest | Testing framework |
| OOP Principles | Class inheritance and polymorphism |

---

## Product Types

### Regular Product
Standard products with name, price, and quantity tracking. Automatically deactivated when out of stock.

### Quantityless Product
Products without quantity limits (e.g., software licenses, digital goods). Always active, no stock tracking.

### Limited Product
Products with purchase quantity restrictions per order (e.g., limited editions).

---

## Promotion Types

| Promotion | Description | Example |
|-----------|-------------|---------|
| **Percentage Discount** | Reduce price by percentage | 20% off MacBook |
| **Second Half Price** | Second item at 50% discount | Buy 2 earbuds, 2nd half price |
| **Third One Free** | Every third item free | Buy 3, get 1 free |

---

## Prerequisites

- Python 3.8 or higher
- No external dependencies (uses Python stdlib only)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/Best-Buy

# No additional installation required (uses Python standard library)
```

---

## Usage

### Running the Application

```bash
python main.py
```

### Menu Options

```
   Store Menu
   ----------
1. List all products in store
2. Show total amount in store
3. Make an order
4. Quit
```

### Making an Order

1. Select option 3 from main menu
2. View available products list
3. Enter product number and quantity
4. Continue adding products or enter empty input to finish
5. View total cost with applied promotions

---

## Project Structure

```
Best-Buy/
├── main.py                   # Main application entry point
├── store.py                  # Store class managing inventory
├── products.py               # Product classes (base and derived)
├── products_promotion.py     # Promotion system classes
├── functions.py              # Helper functions and templates
├── ioput.py                  # Input/output utilities
├── unittest_products.py      # Product class unit tests
├── unittest_store.py         # Store class unit tests
├── product_unittest.py       # Additional product tests
├── requirements.txt          # Dependencies (stdlib only)
└── README.md                 # This file
```

---

## Code Examples

### Creating Products

```python
from products import Product, QuantitativelessProducts, LimitedProducts

# Regular product
laptop = Product("MacBook Air M2", price=1450, quantity=100)

# Quantityless product (digital license)
license = QuantitativelessProducts("Microsoft License", price=100)

# Limited product (max 2 per order)
ferrari = LimitedProducts("Ferrari Model", price=100000, quantity=5, maximum=2)
```

### Applying Promotions

```python
from products_promotion import PercentDiscount, SecondHalfPrice

# 20% discount on MacBook
laptop.promotion = PercentDiscount("20% off MacBook", 20)

# Second item half price on earbuds
earbuds.promotion = SecondHalfPrice("Second Half Price")
```

### Store Operations

```python
from store import Store

# Initialize store with products
my_store = Store([laptop, earbuds, license])

# Get all active products
products = my_store.get_all_products()

# Make an order
order = [(laptop, 1), (earbuds, 2)]
total = my_store.order(order)
```

---

## Class Hierarchy

```
Product (Base Class)
├── Properties: name, price, quantity, active, promotion
├── Methods: buy(), set_quantity(), is_active()
│
├── QuantitativelessProducts
│   └── Overrides: quantity tracking disabled
│
└── LimitedProducts
    └── Adds: maximum purchase limit per order
```

---

## Running Tests

```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest unittest_products.py
python -m unittest unittest_store.py
```

### Test Coverage

- Product initialization and validation
- Quantity management and stock depletion
- Promotion calculation logic
- Store inventory operations
- Order processing with edge cases

---

## Configuration

### Max Stock Entry

Modify in `products.py`:

```python
class Product:
    _max_stock_entry: int = 2000        # Maximum inventory per product
    _max_customer_request: int = 600    # Maximum per order
```

### Default Inventory

Edit `default_inventory()` function in `main.py` to customize starting products.

---

## Error Handling

Custom exception class `ClassMethodException` handles:
- Invalid product names (empty or non-string)
- Negative quantities
- Stock limit violations
- Invalid purchase requests
- Out-of-stock scenarios

---

## Future Enhancements

- Persistent storage (JSON/SQLite database)
- User authentication and order history
- Product categories and filtering
- Dynamic promotion creation
- GUI interface

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
