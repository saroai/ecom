import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
import razorpay
from django.core.mail import send_mail

from .form import ShippingAddressForm
from .models import Order, ShippingAddress, OrderItems
from cart.cart import Cart
from core.shiprocket import create_shiprocket_order


# ─────────────────────────────────────────────
# Checkout — Shipping Address
# ─────────────────────────────────────────────
@login_required
def checkout(request):
    """Step 1: Collect shipping address."""
    cart = Cart(request)
    cart_items = cart.get_items()

    if not cart_items:
        return redirect("cart_summary")

    if request.method == "POST":
        if "apply_coupon" in request.POST:
            coupon_code = request.POST.get("coupon", "").strip().upper()
            if coupon_code == "FIMIKU10":
                request.session["coupon"] = "FIMIKU10"
                messages.success(request, "Coupon FIMIKU10 applied! 10% discount added.")
            else:
                messages.error(request, "Invalid coupon code.")
            return redirect("checkout")
            
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save()
            order   = Order.objects.create(user=request.user, address=address)
            return redirect("billing_info", pk=order.pk)
    else:
        form = ShippingAddressForm()

    total = cart.total()
    coupon_discount = 0
    if request.session.get("coupon") == "FIMIKU10":
        coupon_discount = float(total) * 0.10
    final_total = float(total) - coupon_discount

    context = {
        "form":       form,
        "cart_items": cart_items,
        "total":      total,
        "final_total": final_total,
        "coupon_discount": coupon_discount,
        "applied_coupon": request.session.get("coupon")
    }
    return render(request, "checkout.html", context)


# ─────────────────────────────────────────────
# Billing Info — Review before payment
# ─────────────────────────────────────────────
from django.contrib import messages
from django.shortcuts import redirect

def billing_info(request, pk):
    """Step 2: Show billing summary and Razorpay Pay button."""
    cart  = Cart(request)
    order = get_object_or_404(Order, pk=pk)

    total = cart.total()
    
    # Handle Coupon Submission
    if request.method == "POST":
        coupon_code = request.POST.get("coupon", "").strip().upper()
        if coupon_code == "FIMIKU10":
            request.session["coupon"] = "FIMIKU10"
            messages.success(request, "Coupon FIMIKU10 applied successfully! 10% discount added.")
        else:
            messages.error(request, "Invalid coupon code.")
        return redirect("billing_info", pk=pk)

    # Calculate Discount
    coupon_discount = 0
    if request.session.get("coupon") == "FIMIKU10":
        coupon_discount = float(total) * 0.10
        
    final_total = float(total) - coupon_discount

    context = {
        "cart_items": cart.get_items(),
        "total":      total,
        "final_total": final_total,
        "coupon_discount": coupon_discount,
        "order":      order,
        "delivery":   100,  # flat delivery charge ₹100
        "delivery_discount": 100, # free delivery
        "applied_coupon": request.session.get("coupon")
    }
    return render(request, "billing_info.html", context)


# ────────────────────────────────────────────────────────────────────────────────
# Process Order – Create Razorpay order
# ────────────────────────────────────────────────────────────────────────────────
@login_required
def proccess_order(request, pk):
    """Create Razorpay order and save order items; return JSON for frontend."""
    cart       = Cart(request)
    cart_items = cart.get_items()
    
    total = cart.total()
    coupon_discount = 0
    if request.session.get("coupon") == "FIMIKU10":
        coupon_discount = float(total) * 0.10
        
    total_amount = float(total) - coupon_discount # Free delivery applied and 10% discount

    client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_SECRET_KEY))
    razorpay_order = client.order.create({
        "amount":          int(total_amount) * 100,  # paise
        "currency":        "INR",
        "payment_capture": "1"
    })

    # Save Razorpay order ID and amount
    order = get_object_or_404(Order, pk=pk)
    order.order_id    = razorpay_order["id"]
    order.amount_paid = total_amount
    order.save()

    # Create line items & reduce stock
    for item in cart_items:
        product = item['product']
        qty = item['qty']
        color = item['color']
        
        price = product.discount_price if product.is_discount else product.price
        OrderItems.objects.create(
            order            = order,
            product          = product,
            product_name     = product.name,
            product_price    = price,
            product_qty      = qty,
            product_color    = color,
            product_category = product.category,
        )
        # Decrease stock
        product.stock = max(0, product.stock - int(qty))
        product.save()

    # Build callback URL (HTTPS in production)
    callback_url = request.build_absolute_uri(reverse(settings.RAZOR_PAY_CALLBACK_URL))
    if os.environ.get("ENVIRONMENT") == "production":
        callback_url = callback_url.replace("http://", "https://")

    # Send Notification for New Order Attempt
    try:
        subject = f"New Order Initiated: #{order.pk}"
        message = f"User {request.user.username} ({request.user.email}) has initiated an order for ₹{total_amount}.\nPending payment confirmation."
        send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.ADMIN_EMAIL], fail_silently=True)
    except Exception:
        pass

    return JsonResponse({
        "order_id":      razorpay_order["id"],
        "razorpay_key_id": settings.RAZOR_PAY_KEY_ID,
        "product_name":  request.user.username,
        "amount":        razorpay_order["amount"],
        "callback_url":  callback_url,
    })


# ────────────────────────────────────────────────────────────────────────────────
# Process Order – Cash on Delivery (COD)
# ────────────────────────────────────────────────────────────────────────────────
@login_required
def process_cod_order(request, pk):
    """Process Cash on Delivery order without Razorpay."""
    cart       = Cart(request)
    cart_items = cart.get_items()
    
    total = cart.total()
    coupon_discount = 0
    if request.session.get("coupon") == "FIMIKU10":
        coupon_discount = float(total) * 0.10
        
    total_amount = float(total) - coupon_discount # Free delivery applied and 10% discount

    order = get_object_or_404(Order, pk=pk)
    order.amount_paid = total_amount
    order.payment_id  = "COD"
    order.is_paid     = False
    order.status      = "processing"
    order.save()

    # Create line items & reduce stock
    for item in cart_items:
        product = item['product']
        qty = item['qty']
        color = item['color']
        
        price = product.discount_price if product.is_discount else product.price
        OrderItems.objects.create(
            order            = order,
            product          = product,
            product_name     = product.name,
            product_price    = price,
            product_qty      = qty,
            product_color    = color,
            product_category = product.category,
        )
        # Decrease stock
        product.stock = max(0, product.stock - int(qty))
        product.save()

    import threading

    # Push to Shiprocket asynchronously (it will see payment_id="COD")
    def push_shiprocket(order_obj):
        try:
            create_shiprocket_order(order_obj)
        except Exception as e:
            print("Failed to push to Shiprocket:", e)
            
    threading.Thread(target=push_shiprocket, args=(order,)).start()

    # Update sales counter
    for item in order.items.all():
        if item.product:
            item.product.no_of_sales += item.product_qty
            item.product.save()

    # Clear cart and coupon
    if "session_key" in request.session:
        del request.session["session_key"]
    if "coupon" in request.session:
        del request.session["coupon"]

    # Send Email Notifications asynchronously
    def send_confirmation_email(order_obj):
        try:
            subject = f"Fimiku: COD Order Placed #{order_obj.pk} 🎉"
            message = f"Hello,\n\nYour Cash on Delivery Order #{order_obj.pk} has been successfully placed!\n\nAmount to pay on delivery: ₹{order_obj.amount_paid}\nCustomer: {order_obj.user.username} ({order_obj.user.email})\n\nThank you!"
            send_mail(
                subject, 
                message, 
                settings.EMAIL_HOST_USER, 
                [settings.ADMIN_EMAIL, order_obj.user.email], 
                fail_silently=True
            )
        except Exception as e:
            print("Email failed:", e)
            
    threading.Thread(target=send_confirmation_email, args=(order,)).start()

    # Reuse payment_verify template but indicate COD
    return render(request, "payment_verify.html", {
        "status": "success",
        "order": order,
        "is_cod": True
    })


# ─────────────────────────────────────────────
# Payment Verify — Razorpay Webhook
# ─────────────────────────────────────────────
@csrf_exempt
def payment_verify(request):
    """Verify Razorpay signature; mark order as paid on success."""
    if "razorpay_signature" in request.POST:
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_SECRET_KEY))

        order_id            = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature  = request.POST.get("razorpay_signature")

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id":   order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature":  razorpay_signature,
            })

            # Mark order as paid
            order            = Order.objects.get(order_id=order_id)
            order.is_paid    = True
            order.payment_id = razorpay_payment_id
            order.signature  = razorpay_signature
            order.status     = "processing"
            order.save()

            import threading

            # Push to Shiprocket asynchronously
            def push_shiprocket(order_obj):
                try:
                    create_shiprocket_order(order_obj)
                except Exception as e:
                    print("Failed to push to Shiprocket:", e)
                    
            threading.Thread(target=push_shiprocket, args=(order,)).start()

            # Update sales counter
            for item in order.items.all():
                if item.product:
                    item.product.no_of_sales += item.product_qty
                    item.product.save()

            # Clear cart and coupon
            if "session_key" in request.session:
                del request.session["session_key"]
            if "coupon" in request.session:
                del request.session["coupon"]

            # Send Email Notifications asynchronously
            def send_confirmation_email(order_obj):
                try:
                    subject = f"Fimiku: Payment Confirmed for Order #{order_obj.pk} 🎉"
                    message = f"Hello,\n\nOrder #{order_obj.pk} has been successfully paid and confirmed!\n\nAmount: ₹{order_obj.amount_paid}\nCustomer: {order_obj.user.username} ({order_obj.user.email})\n\nThank you!"
                    send_mail(
                        subject, 
                        message, 
                        settings.EMAIL_HOST_USER, 
                        [settings.ADMIN_EMAIL, order_obj.user.email], 
                        fail_silently=True
                    )
                except Exception as e:
                    print("Email failed:", e)
                    
            threading.Thread(target=send_confirmation_email, args=(order,)).start()

            return render(request, "payment_verify.html", {
                "status":   "success",
                "order":    order,
            })

        except razorpay.errors.SignatureVerificationError:
            return render(request, "payment_verify.html", {"status": "failed", "error": "Signature Verification Failed"})
            
        except Exception as e:
            # Catch any other database or server errors
            import traceback
            error_details = traceback.format_exc()
            return render(request, "payment_verify.html", {"status": "failed", "error": str(e), "details": error_details})

    return render(request, "payment_verify.html", {"status": "invalid", "error": "Invalid Request Method or Missing Data"})


# ─────────────────────────────────────────────
# Update Shipping Address
# ─────────────────────────────────────────────
def update_address(request, order_pk, pk):
    address = get_object_or_404(ShippingAddress, pk=pk)
    form    = ShippingAddressForm(instance=address)

    if request.method == "POST":
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect("billing_info", pk=order_pk)

    return render(request, "checkout.html", {"form": form})
