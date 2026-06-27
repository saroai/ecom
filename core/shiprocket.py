import os
import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger('django')

def get_shiprocket_token():
    """
    Authenticates with Shiprocket API and returns the JWT token.
    Reads credentials from Django settings/env.
    """
    url = "https://apiv2.shiprocket.in/v1/external/auth/login"
    
    email = getattr(settings, 'SHIPROCKET_EMAIL', os.environ.get('SHIPROCKET_EMAIL'))
    password = getattr(settings, 'SHIPROCKET_PASSWORD', os.environ.get('SHIPROCKET_PASSWORD'))
    
    if not email or not password:
        print("Shiprocket credentials are not set in .env")
        return None

    payload = json.dumps({
      "email": email,
      "password": password
    })
    headers = {
      'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("token")
    except Exception as e:
        logger.error(f"Error fetching Shiprocket token: {e}")
        return None

def create_shiprocket_order(order):
    """
    Creates an ad-hoc order in Shiprocket using our Order instance.
    """
    token = get_shiprocket_token()
    if not token:
        return False, "Authentication failed. Check Shiprocket credentials."
        
    url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    
    headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {token}'
    }

    # Format the OrderItems
    order_items = []
    for item in order.items.all():
        order_items.append({
            "name": item.product_name,
            "sku": str(item.product.id)[:10], # Just a fallback if SKU isn't defined
            "units": item.product_qty,
            "selling_price": float(item.product_price),
            "discount": "",
            "tax": "",
            "hsn": ""
        })

    # Prepare Payload
    payload = {
        "order_id": str(order.id),
        "order_date": order.ordered_date.strftime("%Y-%m-%d %H:%M"),
        "pickup_location": "Home", # User's pickup location is Home
        "billing_customer_name": order.address.first_name,
        "billing_last_name": order.address.last_name,
        "billing_address": order.address.address,
        "billing_address_2": "",
        "billing_city": order.address.city,
        "billing_pincode": order.address.pin_code,
        "billing_state": order.address.state,
        "billing_country": order.address.country,
        "billing_email": order.address.email,
        "billing_phone": order.address.phone_no,
        "shipping_is_billing": True,
        "order_items": order_items,
        "payment_method": "Prepaid",
        "sub_total": float(order.amount_paid or 0),
        "length": 10,
        "breadth": 10,
        "height": 10,
        "weight": 0.5
    }

    try:
        logger.info(f"Pushing order {order.id} to Shiprocket...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Save tracking info to our database
        order.shiprocket_order_id = data.get('order_id')
        order.shiprocket_shipment_id = data.get('shipment_id')
        order.save()
        logger.info(f"Shiprocket order created: order_id={data.get('order_id')}, shipment_id={data.get('shipment_id')}")
        
        return True, data
    except Exception as e:
        logger.error(f"Error creating Shiprocket order: {e}")
        try:
            logger.error(f"Shiprocket response: {response.text}")
        except:
            pass
        return False, str(e)

def generate_awb(shipment_id):
    token = get_shiprocket_token()
    if not token:
        return False, "Authentication failed."
    url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = json.dumps({
        "shipment_id": shipment_id
    })
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)

def request_pickup(shipment_id):
    token = get_shiprocket_token()
    if not token:
        return False, "Authentication failed."
    url = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = json.dumps({
        "shipment_id": [shipment_id]
    })
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)

def generate_label(shipment_id):
    token = get_shiprocket_token()
    if not token:
        return False, "Authentication failed."
    url = "https://apiv2.shiprocket.in/v1/external/courier/generate/label"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = json.dumps({
        "shipment_id": [shipment_id]
    })
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)
