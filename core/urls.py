from django.urls import path
from .views import *

urlpatterns = [
    # Homepage
    path("", home, name="home"),

    # Product pages
    path("products/", products, name="products"),
    path("products/<product_cat>/", products, name="products_by_cat"),
    path("product/<id>/", product_detail, name="product"),

    # Wishlist
    path("wishlist/", wishlist, name="wishlist"),
    path("wishlist/toggle/", toggle_wishlist, name="toggle_wishlist"),

    # User orders
    path("my-orders/", your_order, name="your_orders"),
    path("order/<pk>/", order_details, name="order_details"),

    # Admin order management
    path("manage/orders/", order_dashboard, name="order_dashboard"),
    path("manage/orders/update/<pk>/", update_order_status, name="update_order_status"),

    # Static pages
    path("about/", about_us, name="about"),
    path("contact/", contact, name="contact"),
    path("terms/", terms, name="terms"),
    path("privacy/", policy, name="privacy_policy"),
    path("refund/", refund, name="refund"),
]