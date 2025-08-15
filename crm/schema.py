# crm/schema.py

"""
GraphQL schema for the CRM application.

This module defines all GraphQL queries, mutations, and types
related to customer relationship management functionality.
"""

import re
from datetime import datetime
from decimal import Decimal

import graphene
from django.db import transaction
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from crm.filters import CustomerFilter, OrderFilter, ProductFilter
from crm.models import Customer, Order, OrderProduct, Product


# GraphQL Types
class CustomerType(DjangoObjectType):
    """GraphQL type for Customer model."""

    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = ("id", "name", "email", "phone", "created_at", "updated_at")
        filterset_class = CustomerFilter


class ProductType(DjangoObjectType):
    """GraphQL type for Product model."""

    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = ("id", "name", "price", "stock", "created_at", "updated_at")
        filterset_class = ProductFilter


class OrderType(DjangoObjectType):
    """GraphQL type for Order model."""

    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = (
            "id",
            "customer",
            "products",
            "order_date",
            "total_amount",
            "created_at",
            "updated_at",
        )
        filterset_class = OrderFilter


# Input Types
class CustomerInput(graphene.InputObjectType):
    """Input type for creating a customer."""

    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    """Input type for creating a product."""

    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False, default_value=0)


class OrderInput(graphene.InputObjectType):
    """Input type for creating an order."""

    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# Filter Input Types
class CustomerFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    email_icontains = graphene.String()
    created_at_gte = graphene.Date()
    created_at_lte = graphene.Date()
    phone_pattern = graphene.String()


class ProductFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    price_gte = graphene.Decimal()
    price_lte = graphene.Decimal()
    stock_gte = graphene.Int()
    stock_lte = graphene.Int()
    low_stock = graphene.Boolean()


class OrderFilterInput(graphene.InputObjectType):
    total_amount_gte = graphene.Decimal()
    total_amount_lte = graphene.Decimal()
    order_date_gte = graphene.Date()
    order_date_lte = graphene.Date()
    customer_name = graphene.String()
    product_name = graphene.String()
    product_id = graphene.ID()


# Mutation Classes
class CreateCustomer(graphene.Mutation):
    """Mutation to create a single customer."""

    class Arguments:
        input = CustomerInput(required=True)

    # Return fields
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def validate_phone(phone):
        """Validate phone number format."""
        if not phone:
            return True  # Phone is optional

        # Support formats: +1234567890, 123-456-7890, (123) 456-7890
        phone_pattern = (
            r"^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
        )
        return bool(re.match(phone_pattern, phone))

    @staticmethod
    def mutate(root, info, input):
        """Create a new customer."""
        errors = []

        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                errors.append("Email already exists")

            # Validate phone format
            if input.phone and not CreateCustomer.validate_phone(input.phone):
                errors.append(
                    "Phone number must be in format: +1234567890 or 123-456-7890"
                )

            # If there are validation errors, return them
            if errors:
                return CreateCustomer(
                    customer=None,
                    message="Validation failed",
                    success=False,
                    errors=errors,
                )

            # Create the customer
            customer = Customer.objects.create(
                name=input.name, email=input.email, phone=input.phone or None
            )

            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True,
                errors=[],
            )

        except Exception as e:
            return CreateCustomer(
                customer=None,
                message="Failed to create customer",
                success=False,
                errors=[str(e)],
            )


class BulkCreateCustomers(graphene.Mutation):
    """Mutation to create multiple customers."""

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    # Return fields
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    total_count = graphene.Int()

    @staticmethod
    def mutate(root, info, input):
        """Create multiple customers in a single transaction."""
        created_customers = []
        errors = []

        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(
                            f"Row {i + 1}: Email {customer_data.email} already exists"
                        )
                        continue

                    # Validate phone format
                    if customer_data.phone and not CreateCustomer.validate_phone(
                        customer_data.phone
                    ):
                        errors.append(
                            f"Row {i + 1}: Invalid phone format for "
                            f"{customer_data.email}"
                        )
                        continue

                    # Create the customer
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone or None,
                    )
                    created_customers.append(customer)

                except Exception as e:
                    errors.append(f"Row {i + 1}: {str(e)}")

        return BulkCreateCustomers(
            customers=created_customers,
            errors=errors,
            success_count=len(created_customers),
            total_count=len(input),
        )


class CreateProduct(graphene.Mutation):
    """Mutation to create a product."""

    class Arguments:
        input = ProductInput(required=True)

    # Return fields
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        """Create a new product."""
        errors = []

        try:
            # Validate price is positive
            if input.price <= 0:
                errors.append("Price must be positive")

            # Validate stock is not negative
            if input.stock < 0:
                errors.append("Stock cannot be negative")

            # If there are validation errors, return them
            if errors:
                return CreateProduct(
                    product=None,
                    message="Validation failed",
                    success=False,
                    errors=errors,
                )

            # Create the product
            product = Product.objects.create(
                name=input.name, price=input.price, stock=input.stock
            )

            return CreateProduct(
                product=product,
                message="Product created successfully",
                success=True,
                errors=[],
            )

        except Exception as e:
            return CreateProduct(
                product=None,
                message="Failed to create product",
                success=False,
                errors=[str(e)],
            )


class CreateOrder(graphene.Mutation):
    """Mutation to create an order with products."""

    class Arguments:
        input = OrderInput(required=True)

    # Return fields
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        """Create a new order with associated products."""
        errors = []

        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                errors.append(f"Customer with ID {input.customer_id} does not exist")

            # Validate products exist and collect them
            products = []
            if input.product_ids:
                for product_id in input.product_ids:
                    try:
                        product = Product.objects.get(id=product_id)
                        products.append(product)
                    except Product.DoesNotExist:
                        errors.append(f"Product with ID {product_id} does not exist")
            else:
                errors.append("At least one product must be selected")

            # If there are validation errors, return them
            if errors:
                return CreateOrder(
                    order=None,
                    message="Validation failed",
                    success=False,
                    errors=errors,
                )

            # Create the order in a transaction
            with transaction.atomic():
                # Create the order
                order = Order.objects.create(
                    customer=customer, order_date=input.order_date or datetime.now()
                )

                # Add products to the order and calculate total
                total_amount = Decimal("0.00")
                for product in products:
                    OrderProduct.objects.create(
                        order=order,
                        product=product,
                        quantity=1,  # Default quantity for now
                    )
                    total_amount += product.price

                # Update the total amount
                order.total_amount = total_amount
                order.save()

            return CreateOrder(
                order=order,
                message="Order created successfully",
                success=True,
                errors=[],
            )

        except Exception as e:
            return CreateOrder(
                order=None,
                message="Failed to create order",
                success=False,
                errors=[str(e)],
            )


# Query Class
class Query(graphene.ObjectType):
    """
    CRM GraphQL Query class.

    This class contains all query fields available for the CRM application.
    """

    hello = graphene.String(
        description="A simple greeting field that returns 'Hello, GraphQL!'"
    )
    # Customer queries
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        description="Get all customers with filtering and ordering",
        filter=graphene.Argument(CustomerFilterInput),
        order_by=graphene.String(),  # e.g. "name" or "-created_at"
    )
    customer = graphene.Field(
        CustomerType, id=graphene.ID(required=True), description="Get a customer by ID"
    )

    # Product queries
    all_products = DjangoFilterConnectionField(
        ProductType,
        description="Get all products with filtering and ordering",
        filter=graphene.Argument(ProductFilterInput),
        order_by=graphene.String(),  # e.g. "stock" or "-price"
    )
    product = graphene.Field(
        ProductType, id=graphene.ID(required=True), description="Get a product by ID"
    )

    # Order queries
    all_orders = DjangoFilterConnectionField(
        OrderType,
        description="Get all orders with filtering and ordering",
        filter=graphene.Argument(OrderFilterInput),
        order_by=graphene.String(),  # e.g. "order_date" or "-total_amount"
    )
    order = graphene.Field(
        OrderType, id=graphene.ID(required=True), description="Get an order by ID"
    )

    def resolve_hello(self, info):
        """
        Resolver for the hello field.

        Args:
            info: GraphQL execution info object containing request context

        Returns:
            str: Greeting message
        """
        return "Hello, GraphQL!"

    # def resolve_all_customers(self, info):
    #     """Get all customers."""
    #     return Customer.objects.all()

    def resolve_all_customers(self, info, filter=None, order_by=None):
        qs = Customer.objects.all()
        if filter:
            f = {}
            if getattr(filter, "name_icontains", None):
                f["name__icontains"] = filter.name_icontains
            if getattr(filter, "email_icontains", None):
                f["email__icontains"] = filter.email_icontains
            if getattr(filter, "created_at_gte", None):
                f["created_at__gte"] = filter.created_at_gte
            if getattr(filter, "created_at_lte", None):
                f["created_at__lte"] = filter.created_at_lte
            if getattr(filter, "phone_pattern", None):
                val = filter.phone_pattern
                if val.startswith("+"):
                    f["phone__startswith"] = val
                else:
                    f["phone__icontains"] = val
            qs = qs.filter(**f)
        if order_by:
            parts = [p.strip() for p in order_by.split(",") if p.strip()]
            qs = qs.order_by(*parts)
        return qs

    def resolve_customer(self, info, id):
        """Get a customer by ID."""
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    # def resolve_all_products(self, info):
    #     """Get all products."""
    #     return Product.objects.all()

    def resolve_all_products(self, info, filter=None, order_by=None):
        qs = Product.objects.all()
        if filter:
            f = {}
            if getattr(filter, "name_icontains", None):
                f["name__icontains"] = filter.name_icontains
            if getattr(filter, "price_gte", None):
                f["price__gte"] = filter.price_gte
            if getattr(filter, "price_lte", None):
                f["price__lte"] = filter.price_lte
            if getattr(filter, "stock_gte", None):
                f["stock__gte"] = filter.stock_gte
            if getattr(filter, "stock_lte", None):
                f["stock__lte"] = filter.stock_lte
            qs = qs.filter(**f)
            if getattr(filter, "low_stock", None):
                qs = qs.filter(stock__lt=10)
        if order_by:
            parts = [p.strip() for p in order_by.split(",") if p.strip()]
            qs = qs.order_by(*parts)
        return qs

    def resolve_product(self, info, id):
        """Get a product by ID."""
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

    # def resolve_all_orders(self, info):
    #     """Get all orders with related data."""
    #     return (
    #         Order.objects.select_related("customer").prefetch_related("products").all()
    #     )

    def resolve_all_orders(self, info, filter=None, order_by=None):
        qs = Order.objects.select_related("customer").prefetch_related("products").all()
        if filter:
            f = {}
            if getattr(filter, "total_amount_gte", None):
                f["total_amount__gte"] = filter.total_amount_gte
            if getattr(filter, "total_amount_lte", None):
                f["total_amount__lte"] = filter.total_amount_lte
            if getattr(filter, "order_date_gte", None):
                f["order_date__gte"] = filter.order_date_gte
            if getattr(filter, "order_date_lte", None):
                f["order_date__lte"] = filter.order_date_lte
            if getattr(filter, "customer_name", None):
                f["customer__name__icontains"] = filter.customer_name
            if getattr(filter, "product_name", None):
                f["products__name__icontains"] = filter.product_name
            if getattr(filter, "product_id", None):
                f["products__id"] = int(filter.product_id)
            qs = qs.filter(**f)
            if any(k in f for k in ("products__name__icontains", "products__id")):
                qs = qs.distinct()
        if order_by:
            parts = [p.strip() for p in order_by.split(",") if p.strip()]
            qs = qs.order_by(*parts)
        return qs

    def resolve_order(self, info, id):
        """Get an order by ID with related data."""
        try:
            return (
                Order.objects.select_related("customer")
                .prefetch_related("products")
                .get(id=id)
            )
        except Order.DoesNotExist:
            return None


# Mutation Class
class Mutation(graphene.ObjectType):
    """
    CRM GraphQL Mutation class.

    This class contains all mutation fields available for the CRM application.
    """

    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
