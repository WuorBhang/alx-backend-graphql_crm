# crm/schema.py

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# -------------------------------
# 1. Object Types
# -------------------------------

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filter_fields = []
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = []
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = []
        interfaces = (graphene.relay.Node,)


# -------------------------------
# 2. Input Types
# -------------------------------

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# -------------------------------
# 3. Mutations
# -------------------------------

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True
        pattern = r'^(\+\d{1,15}|(\d{3}-\d{3}-\d{4}))$'
        return re.match(pattern, phone) is not None

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists.")

        if input.phone and not CreateCustomer.validate_phone(input.phone):
            raise Exception("Invalid phone number format. Use +1234567890 or 123-456-7890.")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone or ""
        )
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        for idx, data in enumerate(input):
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Email {data.email} already exists.")
                if data.phone and not CreateCustomer.validate_phone(data.phone):
                    raise Exception(f"Invalid phone format for {data.name}.")

                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone or ""
                )
                customers.append(customer)
            except Exception as e:
                errors.append(f"Error at index {idx}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive.")
        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer not found.")

        if not input.product_ids:
            raise Exception("At least one product is required.")

        try:
            product_ids = [from_global_id(pid)[1] if ':' in pid else pid for pid in input.product_ids]
            products = Product.objects.filter(id__in=product_ids)
            if len(products) != len(input.product_ids):
                raise Exception("One or more products not found.")
        except Exception:
            raise Exception("Invalid product ID(s).")

        total = sum(Decimal(p.price) for p in products)
        order = Order.objects.create(customer=customer, total_amount=total)
        order.products.set(products)
        return CreateOrder(order=order)


# -------------------------------
# 4. Query with Filters
# -------------------------------

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter
    )


# -------------------------------
# 5. Mutation Container
# -------------------------------

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
