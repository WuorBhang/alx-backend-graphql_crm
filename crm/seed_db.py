# crm/seed_db.py

"""
Database seeding script for the CRM application.

This script populates the database with sample data for testing
and development purposes.
"""

import os
import sys
from decimal import Decimal

import django
from django.db import transaction

# Ensure the project root is on PATH, then configure Django
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Order, OrderProduct, Product  # noqa: E402


def clear_database():
    """Clear all existing data from the CRM database."""
    print("Clearing existing data...")

    with transaction.atomic():
        OrderProduct.objects.all().delete()
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()

    print("Data cleared successfully")


def create_customers():
    """Create sample customers."""
    print("Creating customers...")

    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "phone": "(555) 123-4567",
        },
        {"name": "David Brown", "email": "david@example.com", "phone": None},
        {"name": "Eva Davis", "email": "eva@example.com", "phone": "+1-555-987-6543"},
    ]

    customers = []
    for customer_data in customers_data:
        customer = Customer.objects.create(**customer_data)
        customers.append(customer)
        print(f"Created customer: {customer.name}")

    print(f"Created {len(customers)} customers")
    return customers


def create_products():
    """Create sample products."""
    print("Creating products...")

    products_data = [
        {"name": "Laptop Pro", "price": Decimal("1299.99"), "stock": 15},
        {"name": "Wireless Mouse", "price": Decimal("29.99"), "stock": 100},
        {"name": "Mechanical Keyboard", "price": Decimal("89.99"), "stock": 50},
        {"name": "USB-C Hub", "price": Decimal("49.99"), "stock": 75},
        {"name": "External Monitor", "price": Decimal("299.99"), "stock": 25},
        {"name": "Webcam HD", "price": Decimal("79.99"), "stock": 40},
        {"name": "Desk Lamp", "price": Decimal("39.99"), "stock": 30},
        {"name": "Ergonomic Chair", "price": Decimal("199.99"), "stock": 10},
    ]

    products = []
    for product_data in products_data:
        product = Product.objects.create(**product_data)
        products.append(product)
        print(f"Created product: {product.name} - ${product.price}")

    print(f"Created {len(products)} products")
    return products


def create_orders(customers, products):
    """Create sample orders with order items."""
    print("Creating orders...")

    orders_data = [
        {
            "customer_index": 0,  # Alice
            "product_indices": [0, 1, 2],  # Laptop, Mouse, Keyboard
        },
        {
            "customer_index": 1,  # Bob
            "product_indices": [3, 4],  # USB-C Hub, Monitor
        },
        {
            "customer_index": 2,  # Carol
            "product_indices": [5, 6],  # Webcam, Desk Lamp
        },
        {
            "customer_index": 3,  # David
            "product_indices": [7],  # Ergonomic Chair
        },
        {
            "customer_index": 4,  # Eva
            "product_indices": [1, 3, 5],  # Mouse, USB-C Hub, Webcam
        },
    ]

    orders = []
    with transaction.atomic():
        for order_data in orders_data:
            customer = customers[order_data["customer_index"]]
            order_products = [products[i] for i in order_data["product_indices"]]

            order = Order.objects.create(customer=customer)

            total_amount = Decimal("0.00")
            for product in order_products:
                quantity = 1

                # Ensure sufficient stock for seeding
                if product.stock < quantity:
                    raise ValueError(
                        f"Insufficient stock for product '{product.name}'. "
                        f"Required: {quantity}, Available: {product.stock}"
                    )

                OrderProduct.objects.create(
                    order=order, product=product, quantity=quantity
                )

                # Decrement stock and persist
                product.stock -= quantity
                product.save(update_fields=["stock"])

                total_amount += product.price * quantity

            # Persist the computed total
            order.total_amount = total_amount
            order.save(update_fields=["total_amount"])

            orders.append(order)
            print(
                f"Created order #{order.pk} for {customer.name} - Total: ${order.total_amount}"
            )

    print(f"Created {len(orders)} orders")
    return orders


def seed():
    """Run the full database seeding process."""
    clear_database()
    customers = create_customers()
    products = create_products()
    create_orders(customers, products)
    print("Seeding completed successfully!")


if __name__ == "__main__":
    seed()
