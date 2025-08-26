"""
Cron jobs for the CRM application
"""
import os
import sys
import django
from datetime import datetime
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
        
        # Optionally verify GraphQL endpoint is responsive
        try:
            # Simple GraphQL query to test endpoint
            query = """
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
            """
            
            response = requests.post(
                'http://localhost:8000/graphql',
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                # Log successful GraphQL response
                with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                    f.write(f"{timestamp} GraphQL endpoint is responsive\n")
            else:
                # Log GraphQL error
                with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                    f.write(f"{timestamp} GraphQL endpoint returned status {response.status_code}\n")
                    
        except requests.exceptions.RequestException as e:
            # Log network error
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
    """Call GraphQL mutation to update low stock products and log results."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mutation = """
    mutation UpdateLowStock {
      updateLowStockProducts {
        products { name stock }
        message
      }
    }
    """
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json().get('data', {}).get('updateLowStockProducts', {})
            products = data.get('products', [])
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] {data.get('message', 'Updated products')}\n")
                for p in products:
                    f.write(f"[{timestamp}] {p.get('name')} -> stock {p.get('stock')}\n")
        else:
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] Mutation failed status {response.status_code}\n")
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Error: {str(e)}\n")
