# seed_db.py (for testing)
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    # Create customers
    c1 = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    c2 = Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890")
    
    # Create products
    p1 = Product.objects.create(name="Laptop", price=999.99, stock=10)
    p2 = Product.objects.create(name="Mouse", price=19.99, stock=50)
    
    # Create orders
    o1 = Order.objects.create(customer=c1, total_amount=1019.98)
    o1.products.add(p1, p2)
    
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
    