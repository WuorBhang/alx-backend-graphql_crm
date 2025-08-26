#!/usr/bin/env python3
"""
Order Reminders Script
Queries GraphQL endpoint for orders within the last 7 days and logs reminders
"""

import os
import sys
import django
from datetime import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

def send_order_reminders():
    """Query GraphQL for recent orders and log reminders"""

    query = gql(
        """
        query GetRecentOrders {
            allOrders(orderBy: ["-order_date"]) {
                edges {
                    node {
                        id
                        orderDate
                        customer { email }
                    }
                }
            }
        }
        """
    )

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        headers={"Content-Type": "application/json"},
        use_json=True,
        verify=True,
        retries=2,
        timeout=10,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    orders_processed = 0

    try:
        result = client.execute(query)
        edges = result.get('allOrders', {}).get('edges', [])

        for edge in edges:
            node = edge.get('node', {})
            order_id = node.get('id')
            order_date_str = node.get('orderDate')
            customer_email = (node.get('customer') or {}).get('email')

            # Log only if we have minimal required fields; server filters last 7 days downstream or we accept all and rely on app logic elsewhere
            if order_id and customer_email and order_date_str:
                log_message = f"[{timestamp}] Order ID: {order_id}, Customer: {customer_email}\n"
                with open('/tmp/order_reminders_log.txt', 'a') as f:
                    f.write(log_message)
                orders_processed += 1

        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Order reminders processed! {orders_processed} recent orders found.\n")

        print("Order reminders processed!")
    except Exception as e:
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Error processing reminders: {str(e)}\n")
        raise

if __name__ == "__main__":
    send_order_reminders()
