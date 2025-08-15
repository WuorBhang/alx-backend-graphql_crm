from django.db import models

# Create your models here.
class User(models.Model):
    """
    Model representing a user in the CRM system.
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.username

class Booking(models.Model):
    """
    Model representing a booking in the CRM system.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateTimeField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Booking for {self.user.username} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"
    
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
