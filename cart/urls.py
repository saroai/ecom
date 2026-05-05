from django.urls import path
from .views import *

urlpatterns = [
   path("cart_add/",cart_add,name="add_cart"),
   path("cart/",cart_summary,name="cart_summary"),
   path("cart_update/",cart_update,name="cart_update"),
   path("delete_cart/",delete_cart,name="delete_cart"),
]