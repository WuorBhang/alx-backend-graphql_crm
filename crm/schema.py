import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError
from django.db import transaction
from graphql import GraphQLError
import re

# Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

    total_amount = graphene.Float()

    def resolve_total_amount(self, info):
        return float(self.total_amount)

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    notes = graphene.String()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            # Validate phone number if provided
            if input.phone and not re.match(r'^\+?\d{10,15}$', input.phone):
                raise GraphQLError("Invalid phone number format. Use +1234567890 or 1234567890")

            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, success=True, message="Customer created successfully")
        except ValidationError as e:
            return CreateCustomer(customer=None, success=False, message=str(e))

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, inputs):
        customers = []
        errors = []
        
        for input in inputs:
            try:
                customer = Customer(
                    name=input.name,
                    email=input.email,
                    phone=input.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(f"Failed to create customer {input.name}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            if input.price <= 0:
                raise GraphQLError("Price must be greater than 0")
            if input.stock and input.stock < 0:
                raise GraphQLError("Stock cannot be negative")
                
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock if input.stock is not None else 0
            )
            product.save()
            return CreateProduct(product=product, success=True, message="Product created successfully")
        except Exception as e:
            return CreateProduct(product=None, success=False, message=str(e))

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
            products = Product.objects.filter(pk__in=input.product_ids)
            
            if not products.exists():
                raise GraphQLError("At least one valid product is required")
                
            order = Order(
                customer=customer,
                total_amount=0,  # Will be calculated in save()
                notes=input.notes
            )
            order.save()
            order.products.set(products)
            order.save()  # Re-save to calculate total
            
            return CreateOrder(order=order, success=True, message="Order created successfully")
        except Customer.DoesNotExist:
            raise GraphQLError("Customer not found")
        except Product.DoesNotExist:
            raise GraphQLError("One or more products not found")
        except Exception as e:
            return CreateOrder(order=None, success=False, message=str(e))

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    customer = graphene.Field(CustomerType, id=graphene.ID())
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    
    product = graphene.Field(ProductType, id=graphene.ID())
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    
    order = graphene.Field(OrderType, id=graphene.ID())
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_customer(self, info, id):
        return Customer.objects.get(pk=id)

    def resolve_product(self, info, id):
        return Product.objects.get(pk=id)

    def resolve_order(self, info, id):
        return Order.objects.get(pk=id)