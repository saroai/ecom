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

        cart.add(product_id,qty)

        return JsonResponse({str(product_id):qty})

    return None


def cart_summary(request):
    cart = Cart(request)

    all_products = cart.products()

    total = cart.total()
    context = {
        "all_products":all_products,
        "total":total,
    }
    return render(request,'cart.html',context)

def cart_update(request):
    if request.POST.get("action") == "post":
        cart = Cart(request)
        product_id = request.POST.get("product_id")
        qty = request.POST.get("qty")

        cart.add(product_id,qty)

        return JsonResponse({})

    return None

def delete_cart(request):

    if request.POST.get("action") == "post":
        cart = Cart(request)
        product_id = request.POST.get("product_id")

        print(product_id)
        cart.delete(product_id)

        return JsonResponse({})

    return None

