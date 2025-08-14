from django.contrib import admin
from .models import Customer, Product, Order

class ProductInline(admin.TabularInline):
    model = Order.products.through
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'total_amount')
    list_filter = ('order_date', 'customer')
    inlines = [ProductInline]
    exclude = ('products',)

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
