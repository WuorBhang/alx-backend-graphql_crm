from django.core.management.base import BaseCommand
from crm.models import Customer, Product, Order
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Clear existing data
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()

        # Create customers
        customers = [
            Customer(name='Alice Johnson', email='alice@example.com', phone='+1234567890'),
            Customer(name='Bob Smith', email='bob@example.com', phone='123-456-7890'),
            Customer(name='Carol Williams', email='carol@example.com'),
        ]
        Customer.objects.bulk_create(customers)

        # Create products
        products = [
            Product(name='Laptop', price=999.99, stock=10),
            Product(name='Smartphone', price=699.99, stock=25),
            Product(name='Headphones', price=149.99, stock=50),
            Product(name='Tablet', price=399.99, stock=5),
        ]
        Product.objects.bulk_create(products)

        # Create orders
        alice = Customer.objects.get(email='alice@example.com')
        bob = Customer.objects.get(email='bob@example.com')
        
        laptop = Product.objects.get(name='Laptop')
        phone = Product.objects.get(name='Smartphone')
        headphones = Product.objects.get(name='Headphones')

        order1 = Order.objects.create(customer=alice, total_amount=laptop.price + phone.price)
        order1.products.set([laptop, phone])

        order2 = Order.objects.create(customer=bob, total_amount=headphones.price * 2)
        order2.products.set([headphones, headphones])

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
        