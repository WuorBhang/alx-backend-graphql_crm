"""
Cron jobs for the CRM application
"""
import os
import sys
import django
from datetime import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import requests

def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM application health
    """
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # Log heartbeat message
        log_message = f"{timestamp} CRM is alive\n"
        
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(log_message)
        
        # Optionally verify GraphQL endpoint is responsive using gql
        try:
            # Simple GraphQL query to test endpoint
            query = gql("""
            query {
                allCustomers {
                    edges {
                        node {
                            id
                            name
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
                timeout=5,
            )
            
            client = Client(transport=transport, fetch_schema_from_transport=False)
            result = client.execute(query)
            
            # Log successful GraphQL response
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(f"{timestamp} GraphQL endpoint is responsive\n")
                    
        except Exception as e:
            # Log GraphQL error
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(f"{timestamp} GraphQL endpoint check failed: {str(e)}\n")
                
    except Exception as e:
        # Log any unexpected errors
        try:
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(f"{timestamp} Heartbeat logging failed: {str(e)}\n")
        except:
            pass  # If we can't even log the error, just continue

def update_low_stock():
    """Call GraphQL mutation to update low stock products and log results using gql."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mutation = gql("""
    mutation UpdateLowStock {
      updateLowStockProducts {
        products { name stock }
        message
      }
    }
    """)
    
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            headers={"Content-Type": "application/json"},
            use_json=True,
            verify=True,
            retries=2,
            timeout=15,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(mutation)
        
        data = result.get('updateLowStockProducts', {})
        products = data.get('products', [])
        
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"[{timestamp}] {data.get('message', 'Updated products')}\n")
            for p in products:
                f.write(f"[{timestamp}] {p.get('name')} -> stock {p.get('stock')}\n")
                
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Error: {str(e)}\n")
