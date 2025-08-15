################
# crm/filters.py
################

import django_filters as filters
from .models import Customer, Product, Order


class CustomerFilter(filters.FilterSet):
    # Custom, human-friendly filters (matched to prompt names)
    nameIcontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    emailIcontains = filters.CharFilter(field_name="email", lookup_expr="icontains")
    createdAtGte = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    createdAtLte = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")
    phonePattern = filters.CharFilter(method="filter_phone_pattern")

    class Meta:
        model = Customer
        fields = []

    def filter_phone_pattern(self, queryset, name, value):
        # e.g. value = "+1" -> startswith +1
        return queryset.filter(phone__startswith=value)


class ProductFilter(filters.FilterSet):
    nameIcontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    priceGte = filters.NumberFilter(field_name="price", lookup_expr="gte")
    priceLte = filters.NumberFilter(field_name="price", lookup_expr="lte")
    stockGte = filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stockLte = filters.NumberFilter(field_name="stock", lookup_expr="lte")

    class Meta:
        model = Product
        fields = []


class OrderFilter(filters.FilterSet):
    totalAmountGte = filters.NumberFilter(field_name="total_amount", lookup_expr="gte")
    totalAmountLte = filters.NumberFilter(field_name="total_amount", lookup_expr="lte")
    orderDateGte = filters.IsoDateTimeFilter(field_name="order_date", lookup_expr="gte")
    orderDateLte = filters.IsoDateTimeFilter(field_name="order_date", lookup_expr="lte")
    customerName = filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    productName = filters.CharFilter(field_name="products__name", lookup_expr="icontains")
    productId = filters.NumberFilter(field_name="products__id")

    class Meta:
        model = Order
        fields = []
