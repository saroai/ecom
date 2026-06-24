import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_com_pro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Product
from payment.models import Order, OrderItems

# 1. Setup Data
User.objects.filter(username="testuser").delete()
user = User.objects.create_user(username="testuser", password="password", email="test@test.com")

product = Product.objects.filter(stock__gt=0).first()
if not product:
    print("No products in DB!")
    exit(1)

print(f"Using Product: {product.name} ({product.id})")

# 2. Test Client
c = Client(HTTP_HOST='localhost')
c.login(username="testuser", password="password")

# 3. Add to Cart
response = c.post('/cart_add/', {
    'action': 'post',
    'product_id': str(product.id),
    'qty': '1',
    'color': 'Red'
})
print("Add to Cart Status:", response.status_code)

# 4. Checkout Step 1: Shipping Address
response = c.post('/payment/checkout/', {
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@doe.com',
    'address': '123 Main St',
    'city': 'Test City',
    'state': 'TS',
    'pin_code': '123456',
    'phone_no': '9999999999',
    'country': 'India'
}, follow=True)
print("Checkout Shipping Status:", response.status_code)

# Get the created order
order = Order.objects.filter(user=user).last()
print("Order created:", order.id if order else "Failed")

# 5. Process Order (Razorpay creation)
from unittest.mock import patch

with patch('razorpay.Client') as MockClient:
    mock_instance = MockClient.return_value
    mock_instance.order.create.return_value = {"id": "order_test123", "amount": 20000}
    
    response = c.post(f'/payment/process_order/{order.id}/')
    print("Process Order Status:", response.status_code)
    
    # 6. Payment Verify
    mock_instance.utility.verify_payment_signature.return_value = True
    
    response = c.post('/payment/payment_verify/', {
        'razorpay_order_id': 'order_test123',
        'razorpay_payment_id': 'pay_test123',
        'razorpay_signature': 'fake_signature'
    })
    print("Payment Verify Status:", response.status_code)

# 7. Check Admin Panel Storage (Database)
order.refresh_from_db()
print("============== TEST RESULTS ==============")
print(f"Final Order Status: {order.status}, Paid: {order.is_paid}, Payment ID: {order.payment_id}")
order_items = OrderItems.objects.filter(order=order)
print(f"Order Items Saved: {order_items.count()}")
for item in order_items:
    print(f"- {item.product_name}: Qty {item.product_qty}, Color {item.product_color}")
print("==========================================")
