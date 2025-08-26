#!/bin/bash

# Customer Cleanup Script
# Deletes customers with no orders since a year ago

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Execute Django command to delete inactive customers
python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Calculate date 1 year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
customers_to_delete = []
for customer in Customer.objects.all():
    # Check if customer has any orders in the last year
    recent_orders = Order.objects.filter(
        customer=customer,
        order_date__gte=one_year_ago
    )
    if not recent_orders.exists():
        customers_to_delete.append(customer)

# Delete inactive customers
deleted_count = len(customers_to_delete)
for customer in customers_to_delete:
    customer.delete()

print(f'Deleted {deleted_count} inactive customers')
"

# Log the results
echo "[$TIMESTAMP] Customer cleanup completed. Check Django output above for details." >> /tmp/customer_cleanup_log.txt
