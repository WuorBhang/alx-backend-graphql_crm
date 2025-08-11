# crm/seed_db.py

from crm.models import Customer, Product, Order

def seed():
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    # Create customers
    alice = Customer.objects.create(
        name="Alice",
        email="alice@example.com",
        phone="+1234567890"
    )
    bob = Customer.objects.create(
        name="Bob",
        email="bob@example.com",
        phone="123-456-7890"
    )

    # Create products
    laptop = Product.objects.create(
        name="Laptop",
        price=999.99,
        stock=5
    )
    mouse = Product.objects.create(
        name="Mouse",
        price=25.50,
        stock=50
    )

    # Create order
    order = Order.objects.create(
        customer=alice,
        total_amount=1025.49
    )
    order.products.set([laptop, mouse])

    print("✅ Database seeded with sample data!")
    