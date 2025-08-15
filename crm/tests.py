# crm/tests.py

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

# from graphene_django.utils.testing import GraphQLTestCase
# from alx_backend_graphql_crm.schema import schema
from crm.filters import CustomerFilter, OrderFilter, ProductFilter
from crm.models import Customer, Order, OrderProduct, Product


class CustomerModelTest(TestCase):
    def test_create_customer_success(self):
        customer = Customer.objects.create(
            name="John Doe", email="john@example.com", phone="+1234567890"
        )
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertTrue(customer.phone.startswith("+"))

    def test_unique_email_constraint(self):
        Customer.objects.create(name="Jane", email="jane@example.com")
        with self.assertRaises(Exception):
            Customer.objects.create(name="Jane2", email="jane@example.com")

    def test_phone_validation(self):
        with self.assertRaises(ValidationError):
            customer = Customer(
                name="Bad Phone", email="badphone@example.com", phone="notaphone"
            )
            customer.full_clean()


class ProductModelTest(TestCase):
    def test_create_product_success(self):
        product = Product.objects.create(name="Widget", price=Decimal("10.00"), stock=5)
        self.assertEqual(product.price, Decimal("10.00"))
        self.assertEqual(product.stock, 5)

    def test_negative_price_validation(self):
        product = Product(name="Bad", price=Decimal("-1.00"), stock=1)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_stock_validation(self):
        product = Product(name="Bad", price=Decimal("1.00"), stock=-1)
        with self.assertRaises(ValidationError):
            product.full_clean()


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Orderer", email="orderer@example.com"
        )
        self.product1 = Product.objects.create(
            name="P1", price=Decimal("5.00"), stock=10
        )
        self.product2 = Product.objects.create(
            name="P2", price=Decimal("15.00"), stock=10
        )

    def test_order_total_calculation(self):
        order = Order.objects.create(customer=self.customer)
        OrderProduct.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price_at_purchase=self.product1.price,
        )
        OrderProduct.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            price_at_purchase=self.product2.price,
        )
        total = order.calculate_total()
        self.assertEqual(total, self.product1.price + self.product2.price)

    def test_order_total_negative_validation(self):
        order = Order(customer=self.customer, total_amount=Decimal("-10.00"))
        with self.assertRaises(ValidationError):
            order.full_clean()


class OrderProductModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Orderer", email="orderer2@example.com"
        )
        self.product = Product.objects.create(name="P1", price=Decimal("5.00"), stock=1)
        self.order = Order.objects.create(customer=self.customer)

    def test_quantity_exceeds_stock(self):
        op = OrderProduct(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_purchase=self.product.price,
        )
        with self.assertRaises(ValidationError):
            op.full_clean()

    def test_price_at_purchase_set(self):
        op = OrderProduct(order=self.order, product=self.product, quantity=1)
        op.clean()
        self.assertEqual(op.price_at_purchase, self.product.price)


# Filter tests (example for Customer)
class CustomerFilterTest(TestCase):
    def setUp(self):
        Customer.objects.create(
            name="Alice", email="alice@example.com", phone="+111111111"
        )
        Customer.objects.create(
            name="Bob", email="bob@example.com", phone="222-222-2222"
        )

    def test_filter_by_name(self):
        f = CustomerFilter({"name": "Alice"}, queryset=Customer.objects.all())
        self.assertEqual(f.qs.count(), 1)

    def test_filter_by_phone_pattern(self):
        f = CustomerFilter({"phone_pattern": "+"}, queryset=Customer.objects.all())
        self.assertEqual(f.qs.count(), 1)


# ProductFilter tests
class ProductFilterTest(TestCase):
    def setUp(self):
        Product.objects.create(name="Widget", price=10, stock=5)
        Product.objects.create(name="Gadget", price=20, stock=2)

    def test_filter_by_name(self):
        f = ProductFilter({"name": "Widget"}, queryset=Product.objects.all())
        self.assertEqual(f.qs.count(), 1)

    def test_filter_low_stock(self):
        f = ProductFilter({"low_stock": True}, queryset=Product.objects.all())
        self.assertEqual(f.qs.count(), 2)  # Both have stock < 10


# OrderFilter tests
class OrderFilterTest(TestCase):
    def setUp(self):
        c = Customer.objects.create(name="C", email="c@example.com")
        p = Product.objects.create(name="P", price=10, stock=5)
        o = Order.objects.create(customer=c, total_amount=10)
        # Through model with required fields:
        OrderProduct.objects.create(
            order=o, product=p, quantity=1, price_at_purchase=p.price
        )

    def test_filter_by_total_amount(self):
        f = OrderFilter({"total_amount__gte": 5}, queryset=Order.objects.all())
        self.assertEqual(f.qs.count(), 1)


# class CustomerGraphQLTest(GraphQLTestCase):
#     GRAPHQL_SCHEMA = schema

#     def test_create_customer_mutation(self):
#         response = self.query(
#             """
#             mutation {
#                 createCustomer(input: {name: "Test", email: "test@example.com", phone: "+1234567890"}) {
#                     success
#                     customer { id name email }
#                     errors
#                 }
#             }
#             """
#         )
#         print("GraphQL response:", response.content)
#         self.assertResponseNoErrors(response)
#         self.assertTrue(response.json()["data"]["createCustomer"]["success"])
