# crm/filters.py
import django_filters as df

from crm.models import Customer, Order, Product


class CustomerFilter(df.FilterSet):
    name = df.CharFilter(field_name="name", lookup_expr="icontains")
    email = df.CharFilter(field_name="email", lookup_expr="icontains")
    created_at__gte = df.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at__lte = df.DateFilter(field_name="created_at", lookup_expr="lte")
    phone_pattern = df.CharFilter(method="filter_phone_pattern")

    class Meta:
        model = Customer
        fields = []

    def filter_phone_pattern(self, queryset, name, value):
        if value.startswith("+"):
            return queryset.filter(phone__startswith=value)
        return queryset.filter(phone__icontains=value)


class ProductFilter(df.FilterSet):
    name = df.CharFilter(field_name="name", lookup_expr="icontains")
    price__gte = df.NumberFilter(field_name="price", lookup_expr="gte")
    price__lte = df.NumberFilter(field_name="price", lookup_expr="lte")
    stock__gte = df.NumberFilter(field_name="stock", lookup_expr="gte")
    stock__lte = df.NumberFilter(field_name="stock", lookup_expr="lte")
    low_stock = df.BooleanFilter(method="filter_low_stock")

    class Meta:
        model = Product
        fields = []

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(df.FilterSet):
    total_amount__gte = df.NumberFilter(field_name="total_amount", lookup_expr="gte")
    total_amount__lte = df.NumberFilter(field_name="total_amount", lookup_expr="lte")
    order_date__gte = df.DateFilter(field_name="order_date", lookup_expr="gte")
    order_date__lte = df.DateFilter(field_name="order_date", lookup_expr="lte")
    customer_name = df.CharFilter(field_name="customer__name", lookup_expr="icontains")
    product_name = df.CharFilter(field_name="products__name", lookup_expr="icontains")
    product_id = df.NumberFilter(field_name="products__id")

    class Meta:
        model = Order
        fields = []
