# crm/models.py

"""
CRM application models.

This module contains all database models related to customer
relationship management functionality.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all CRM models.

    Fields:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(BaseModel):
    """
    Customer model for storing customer information.

    Fields:
        name: Customer's full name
        email: Customer's email address (unique)
        phone: Customer's phone number (optional)
    """

    # Phone number validator supporting multiple formats
    phone_validator = RegexValidator(
        regex=r"^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
        message="Phone number must be in format: +1234567890 or 123-456-7890",
    )

    name = models.CharField(max_length=100, help_text="Customer's full name")
    email = models.EmailField(unique=True, help_text="Customer's email address")
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        help_text="Customer's phone number (optional)",
    )

    class Meta:
        db_table = "crm_customer"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["name"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.email})"


class Product(BaseModel):
    """
    Product model for storing product information.

    Fields:
        name: Product name
        price: Product price (positive decimal)
        stock: Available stock quantity (non-negative integer)
    """

    name = models.CharField(max_length=200, help_text="Product name")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Product price",
    )
    stock = models.PositiveIntegerField(default=0, help_text="Available stock quantity")

    class Meta:
        db_table = "crm_product"
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} - ${self.price}"

    def clean(self):
        """Validate that price is positive."""

        if self.price <= 0:
            raise ValidationError("Price must be positive")


class Order(BaseModel):
    """
    Order model for storing customer orders.

    Fields:
        customer: Reference to the customer who placed the order
        products: Reference to the customer's products order
        order_date: Date when the order was placed
        total_amount: Total amount of the order (calculated from products)
    """

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Customer who placed the order",
    )
    products = models.ManyToManyField(
        Product,
        through="OrderProduct",
        related_name="orders",
        help_text="Products included in this order",
    )
    order_date = models.DateTimeField(
        auto_now_add=True, help_text="Date when the order was placed"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total amount of the order",
    )

    class Meta:
        db_table = "crm_order"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        indexes = [
            models.Index(fields=["customer", "-order_date"]),
            models.Index(fields=["order_date"]),
            models.Index(fields=["total_amount"]),
        ]
        ordering = ["-order_date"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.name} - ${self.total_amount}"

    def clean(self) -> None:
        """Custom validation logic for Order model."""
        super().clean()

        # Validate total amount is not negative
        if self.total_amount is not None and self.total_amount < 0:
            raise ValidationError({"total_amount": "Total amount cannot be negative"})

    def calculate_total(self):
        """Calculate the total amount based on associated products."""
        total = sum(product.price for product in self.products.all())
        self.total_amount = total
        return total

    def save(self, *args, **kwargs):
        """Override save to ensure total_amount is calculated if not provided."""
        # For new orders without total_amount, we'll set it after products are added
        super().save(*args, **kwargs)


class OrderProduct(models.Model):
    """
    Through model for the many-to-many relationship between Order and Product.

    This allows us to store additional information about each product in an order,
    such as quantity (for future enhancement).
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_products",
        help_text="Order this item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_products",
        help_text="Product being ordered",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of this product in the order",
    )
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price of the product at the time of purchase",
    )

    class Meta:
        db_table = "crm_order_product"
        unique_together = ("order", "product")
        verbose_name = "Order Product"
        verbose_name_plural = "Order Products"

    def __str__(self):
        return f"Order #: {self.order} - {self.product} (qty: {self.quantity})"

    def clean(self):
        """
        Custom validation for the OrderItem model.
        """
        # Ensure the product has enough stock
        if self.quantity > self.product.stock:
            raise ValidationError(
                {"quantity": f"Not enough stock. Only {self.product.stock} available."}
            )

        # Set the price at purchase to the current product price if not set
        if not self.price_at_purchase:
            self.price_at_purchase = self.product.price

    def save(self, *args, **kwargs):
        """
        Override save to update the order total amount.
        """
        if not self.pk:  # Only on creation
            self.price_at_purchase = self.product.price

        super().save(*args, **kwargs)
        self.order.calculate_total()
