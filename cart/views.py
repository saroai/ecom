from django.shortcuts import render
from django.http import JsonResponse
from .cart import Cart
from core.models import Product

# Create your views here.
def cart_add(request):
    cart = Cart(request)

    if request.POST.get("action") == "post":
        product_id = request.POST.get("product_id")
        qty = request.POST.get("qty")
        color = request.POST.get("color", "")

        print("POST TO CART ADD:", product_id, qty, color)
        cart.add(product_id, qty, color)

        return JsonResponse({'qty': len(cart)})

    return None


def cart_summary(request):
    cart = Cart(request)

    cart_items = cart.get_items()
    print("SESSION KEY:", request.session.session_key)
    print("CART CONTENTS IN SESSION:", request.session.get("session_key"))
    print("CART ITEMS RETURNED:", cart_items)
    total = cart.total()
    context = {
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, 'cart.html', context)

def cart_update(request):
    if request.POST.get("action") == "post":
        cart = Cart(request)
        product_id = request.POST.get("product_id")
        qty = request.POST.get("qty")
        color = request.POST.get("color", "")

        cart.add(product_id, qty, color)

        return JsonResponse({})

    return None

def delete_cart(request):
    if request.POST.get("action") == "post":
        cart = Cart(request)
        cart_key = request.POST.get("cart_key")

        if not cart_key:
            # Fallback for older code testing
            cart_key = request.POST.get("product_id")

        cart.delete(cart_key)

        return JsonResponse({})

    return None
