from celery import shared_task
from datetime import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    """Generate a weekly CRM report with total customers, orders, and revenue."""
    try:
        query = gql("""
        query GetCRMSummary {
            allCustomers {
                edges {
                    node {
                        id
                    }
                }
            }
            allOrders {
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """)
        
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            headers={"Content-Type": "application/json"},
            use_json=True,
            verify=True,
            retries=2,
            timeout=15,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(query)
        
        # Count customers from edges
        customers_data = result.get('allCustomers', {}).get('edges', [])
        total_customers = len(customers_data)
        
        # Count orders and calculate revenue from edges
        orders_data = result.get('allOrders', {}).get('edges', [])
        total_orders = len(orders_data)
        
        total_revenue = sum(
            float(edge['node']['totalAmount']) 
            for edge in orders_data 
            if edge['node']['totalAmount'] is not None
        )
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(report_message)
        
        logger.info(f"CRM Report generated: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue")
        
        return {
            'customers': total_customers,
            'orders': total_orders,
            'revenue': total_revenue,
            'timestamp': timestamp
        }
        
    except Exception as e:
        error_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error generating CRM report: {str(e)}\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_message)
        
        logger.error(f"Error generating CRM report: {str(e)}")
        raise
