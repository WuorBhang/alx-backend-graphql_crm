# crm/admin.py

"""
Django admin configuration for CRM models.

This module registers CRM models with the Django admin interface
to provide a web-based administrative interface.
"""

from django.contrib import admin

from .models import Customer, Order, OrderProduct, Product


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for Customer model."""

    list_display = ("name", "email", "phone", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Customer Information", {"fields": ("name", "email", "phone")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""

    list_display = ("name", "price", "stock", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Product Information", {"fields": ("name", "price", "stock")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class OrderProductInline(admin.TabularInline):
    """Inline admin for OrderProduct model."""

    model = OrderProduct
    extra = 1
    readonly_fields = ("quantity",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""

    list_display = ("id", "customer", "total_amount", "order_date")
    list_filter = ("order_date", "created_at")
    search_fields = ("customer__name", "customer__email")
    readonly_fields = ("order_date", "total_amount", "created_at", "updated_at")
    inlines = [OrderProductInline]

    fieldsets = (
        ("Order Information", {"fields": ("customer", "order_date", "total_amount")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        queryset = super().get_queryset(request)
        return queryset.select_related("customer")


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    """Admin configuration for OrderProduct model."""

    list_display = ("order", "product", "quantity")
    list_filter = ("order__order_date",)
    search_fields = ("order__customer__name", "product__name")

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        queryset = super().get_queryset(request)
        return queryset.select_related("order__customer", "product")
