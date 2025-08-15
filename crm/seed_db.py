#################
# seed_db.py     #  (Quick seeding for local testing)
#################

import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order  # noqa: E402


def run():
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    alice = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    bob = Customer.objects.create(name="Bob", email="bob@example.com")

    laptop = Product.objects.create(name="Laptop", price=Decimal("999.99"), stock=10)
    mouse = Product.objects.create(name="Mouse", price=Decimal("25.50"), stock=100)

    o1 = Order.objects.create(customer=alice)
    o1.products.set([laptop, mouse])
    o1.recalc_total()

    print("Seeded: ", Customer.objects.count(), "customers;", Product.objects.count(), "products;", Order.objects.count(), "orders")


if __name__ == "__main__":
    run()
