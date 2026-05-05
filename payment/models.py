import uuid
from django.db import models
from django.contrib.auth.models import User
from core.models import Product


# ─────────────────────────────────────────────
# Shipping Address
# ─────────────────────────────────────────────
class ShippingAddress(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255)
    address    = models.CharField(max_length=500)
    city       = models.CharField(max_length=255)
    state      = models.CharField(max_length=255)
    pin_code   = models.CharField(max_length=10)
    country    = models.CharField(max_length=255, default="India")
    phone_no   = models.CharField(max_length=15)
    email      = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} – {self.city}"


# ─────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────
class Order(models.Model):
    """Tracks the full lifecycle of a customer order."""

    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("processing","Processing"),
        ("shipped",   "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="orders")
    address     = models.OneToOneField(ShippingAddress, on_delete=models.RESTRICT)

    # Razorpay fields
    order_id    = models.CharField(max_length=255, null=True, blank=True, editable=False)
    payment_id  = models.CharField(max_length=255, null=True, blank=True, editable=False)
    signature   = models.CharField(max_length=255, null=True, blank=True, editable=False)

    amount_paid = models.PositiveBigIntegerField(null=True, blank=True)
    is_paid     = models.BooleanField(default=False)

    # Order status for admin management
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    ordered_date = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ordered_date"]

    def __str__(self):
        return f"Order #{str(self.id)[:8]} – {self.user.username}"


# ─────────────────────────────────────────────
# Order Items
# ─────────────────────────────────────────────
class OrderItems(models.Model):
    """Individual line items within an order."""
    order         = models.ForeignKey(Order, on_delete=models.RESTRICT, related_name="items")
    product       = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name  = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=8, decimal_places=2)
    product_qty   = models.IntegerField()
    product_category = models.CharField(max_length=50, blank=True)

    def line_total(self):
        if self.product_price is not None and self.product_qty is not None:
            return self.product_price * self.product_qty
        return 0

    def __str__(self):
        return f"{self.product_name} x{self.product_qty}"
