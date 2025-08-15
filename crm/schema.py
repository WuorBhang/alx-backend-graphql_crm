# crm/schema.py
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError
import re

# Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter

# Inputs
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        try:
            # Validate phone format
            if input.phone and not re.match(r'^(\+\d{1,3}[- ]?)?\d{3}[- ]?\d{3}[- ]?\d{4}$', input.phone):
                raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890")
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except Exception as e:
            return CreateCustomer(customer=None, errors=[str(e)])

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, inputs):
        customers = []
        errors = []
        for input in inputs:
            try:
                # Validate phone format
                if input.phone and not re.match(r'^(\+\d{1,3}[- ]?)?\d{3}[- ]?\d{3}[- ]?\d{4}$', input.phone):
                    raise ValidationError("Invalid phone format")
                
                customer = Customer(
                    name=input.name,
                    email=input.email,
                    phone=input.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(f"{input.email}: {str(e)}")
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        try:
            # Validate price and stock
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            if input.stock and input.stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock if input.stock is not None else 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except Exception as e:
            return CreateProduct(product=None, errors=[str(e)])

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError("Customer does not exist")
            
            # Validate products exist
            products = []
            total_amount = 0
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                    total_amount += product.price
                except Product.DoesNotExist:
                    raise ValidationError(f"Product with ID {product_id} does not exist")
            
            if not products:
                raise ValidationError("At least one product is required")
            
            order = Order(
                customer=customer,
                total_amount=total_amount,
                order_date=input.order_date if input.order_date else None
            )
            order.save()
            order.products.set(products)
            return CreateOrder(order=order)
        except Exception as e:
            return CreateOrder(order=None, errors=[str(e)])

# Query
class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"

# Mutation
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    