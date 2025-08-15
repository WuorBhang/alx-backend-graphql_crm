################
# crm/schema.py #  (Tasks 1–3)
################

import re
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import from_global_id

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# -----------------
# GraphQL Types
# -----------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        fields = ("id", "name", "email", "phone", "created_at", "updated_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = ("id", "name", "price", "stock", "created_at", "updated_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = (
            "id",
            "customer",
            "products",
            "total_amount",
            "order_date",
            "created_at",
            "updated_at",
        )


# -----------------
# Inputs (Filters)
# -----------------
class CustomerFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    emailIcontains = graphene.String()
    createdAtGte = graphene.String()
    createdAtLte = graphene.String()
    phonePattern = graphene.String()


class ProductFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    priceGte = graphene.Float()
    priceLte = graphene.Float()
    stockGte = graphene.Int()
    stockLte = graphene.Int()


class OrderFilterInput(graphene.InputObjectType):
    totalAmountGte = graphene.Float()
    totalAmountLte = graphene.Float()
    orderDateGte = graphene.String()
    orderDateLte = graphene.String()
    customerName = graphene.String()
    productName = graphene.String()
    productId = graphene.ID()


# -----------------
# Mutations (Task 1/2)
# -----------------
PHONE_RE = re.compile(r"^(\+?\d[\d\-]{7,})$")


class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.NonNull(graphene.String)
    email = graphene.NonNull(graphene.String)
    phone = graphene.String()


class CreateCustomerPayload(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = graphene.NonNull(CreateCustomerInput)

    Output = CreateCustomerPayload

    @staticmethod
    def mutate(root, info, input: CreateCustomerInput):
        errors = []
        name = input.get("name").strip()
        email = input.get("email").lower().strip()
        phone = input.get("phone")

        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists")
        if phone:
            if not PHONE_RE.match(phone):
                errors.append("Invalid phone format")
        if errors:
            return CreateCustomerPayload(customer=None, message=None, errors=errors)

        customer = Customer.objects.create(name=name, email=email, phone=phone or "")
        return CreateCustomerPayload(customer=customer, message="Customer created", errors=[])


class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.NonNull(graphene.String)
    email = graphene.NonNull(graphene.String)
    phone = graphene.String()


class BulkCreateCustomersPayload(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.NonNull(graphene.List(graphene.NonNull(BulkCustomerInput)))

    Output = BulkCreateCustomersPayload

    @staticmethod
    def mutate(root, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for idx, c in enumerate(input):
                name = c.get("name", "").strip()
                email = c.get("email", "").lower().strip()
                phone = c.get("phone")

                if not name or not email:
                    errors.append(f"Row {idx}: name and email are required")
                    continue
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Row {idx}: Email already exists")
                    continue
                if phone and not PHONE_RE.match(phone):
                    errors.append(f"Row {idx}: Invalid phone format")
                    continue
                created.append(Customer(name=name, email=email, phone=phone or ""))

            # Create valid ones
            Customer.objects.bulk_create(created)
        # Re-fetch to return with IDs
        emails = [c.email for c in created]
        customers = list(Customer.objects.filter(email__in=emails))
        return BulkCreateCustomersPayload(customers=customers, errors=errors)


class CreateProductInput(graphene.InputObjectType):
    name = graphene.NonNull(graphene.String)
    price = graphene.NonNull(graphene.Float)
    stock = graphene.Int(default_value=0)


class CreateProductPayload(graphene.ObjectType):
    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = graphene.NonNull(CreateProductInput)

    Output = CreateProductPayload

    @staticmethod
    def mutate(root, info, input: CreateProductInput):
        name = input.get("name").strip()
        price = Decimal(str(input.get("price")))
        stock = int(input.get("stock") or 0)
        errors = []
        if price <= 0:
            errors.append("Price must be positive")
        if stock < 0:
            errors.append("Stock cannot be negative")
        if errors:
            return CreateProductPayload(product=None, errors=errors)
        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProductPayload(product=product, errors=[])


class CreateOrderInput(graphene.InputObjectType):
    customerId = graphene.NonNull(graphene.ID)
    productIds = graphene.NonNull(graphene.List(graphene.NonNull(graphene.ID)))
    orderDate = graphene.String()  # ISO string; optional


class CreateOrderPayload(graphene.ObjectType):
    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = graphene.NonNull(CreateOrderInput)

    Output = CreateOrderPayload

    @staticmethod
    def mutate(root, info, input: CreateOrderInput):
        errors = []
        try:
            _, customer_dbid = from_global_id(input["customerId"])  # Relay global ID -> DB ID
        except Exception:
            return CreateOrderPayload(order=None, errors=["Invalid customer ID"])

        product_dbids = []
        for pid in input["productIds"]:
            try:
                _, dbid = from_global_id(pid)
                product_dbids.append(int(dbid))
            except Exception:
                errors.append("Invalid product ID")
        if errors:
            return CreateOrderPayload(order=None, errors=errors)

        try:
            customer = Customer.objects.get(id=int(customer_dbid))
        except Customer.DoesNotExist:
            return CreateOrderPayload(order=None, errors=["Customer not found"])

        products = list(Product.objects.filter(id__in=product_dbids))
        if not products:
            return CreateOrderPayload(order=None, errors=["At least one valid product is required"])
        if len(products) != len(set(product_dbids)):
            # Some IDs invalid
            missing = set(product_dbids) - set(p.id for p in products)
            return CreateOrderPayload(order=None, errors=[f"Invalid product ID(s): {sorted(missing)}"])

        order_date = timezone.now()
        if input.get("orderDate"):
            try:
                order_date = timezone.datetime.fromisoformat(input["orderDate"])  # naive OK; auto-add tz
                if timezone.is_naive(order_date):
                    order_date = timezone.make_aware(order_date, timezone=timezone.utc)
            except Exception:
                return CreateOrderPayload(order=None, errors=["Invalid order_date format; use ISO-8601"])

        with transaction.atomic():
            order = Order.objects.create(customer=customer, order_date=order_date)
            order.products.set(products)
            # Calculate sum of product prices
            total = sum((p.price for p in products), Decimal("0.00"))
            order.total_amount = total
            order.save(update_fields=["total_amount"])

        return CreateOrderPayload(order=order, errors=[])


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# -----------------
# Queries (Task 3: filtering + ordering)
# -----------------
class Query(graphene.ObjectType):
    # Relay connections to match edges/node shape in the prompt
    all_customers = relay.ConnectionField(
        CustomerType._meta.connection,
        filter=CustomerFilterInput(),
        orderBy=graphene.String(),
    )
    all_products = relay.ConnectionField(
        ProductType._meta.connection,
        filter=ProductFilterInput(),
        orderBy=graphene.String(),
    )
    all_orders = relay.ConnectionField(
        OrderType._meta.connection,
        filter=OrderFilterInput(),
        orderBy=graphene.String(),
    )

    def resolve_all_customers(root, info, filter=None, orderBy=None, **kwargs):
        qs = Customer.objects.all().order_by("id")
        if filter is not None:
            fs = CustomerFilter(data=filter, queryset=qs)
            qs = fs.qs
        if orderBy:
            qs = qs.order_by(orderBy)
        return qs

    def resolve_all_products(root, info, filter=None, orderBy=None, **kwargs):
        qs = Product.objects.all().order_by("id")
        if filter is not None:
            fs = ProductFilter(data=filter, queryset=qs)
            qs = fs.qs
        if orderBy:
            qs = qs.order_by(orderBy)
        return qs

    def resolve_all_orders(root, info, filter=None, orderBy=None, **kwargs):
        qs = Order.objects.select_related("customer").prefetch_related("products").all().order_by("id")
        if filter is not None:
            # Convert global productId to DB ID if present
            if filter.get("productId"):
                try:
                    _, dbid = from_global_id(filter["productId"])
                    filter = {**filter, "productId": int(dbid)}
                except Exception:
                    # Leave as-is; FilterSet will make it empty
                    pass
            fs = OrderFilter(data=filter, queryset=qs)
            qs = fs.qs.distinct()
        if orderBy:
            qs = qs.order_by(orderBy)
        return qs

