from django.urls import path
from .views import *

urlpatterns = [
  path("checkout/", checkout, name="checkout"),
  path("billinginfo/<pk>/", billing_info, name="billing_info"),
  path("process_order/<pk>/", proccess_order, name="proccess_order"),
  path("payment_verify/", payment_verify, name="payment_verify"),
  path("update_address/<order_pk>/<pk>/", update_address, name="update_address"),
]