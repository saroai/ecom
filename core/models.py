import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ─────────────────────────────────────────────
# Product Model — Toy E-Commerce
# ─────────────────────────────────────────────
class Product(models.Model):
    """Toy product with category, age group, stock, and multi-image support."""

    # Category choices
    CATEGORY_CHOICES = [
        ("teething", "Teething Toys"),
        ("bath",     "Bath Toys"),
        ("feeding",  "Feeding Accessories"),
        ("sensory",  "Sensory Learning"),
        ("play",     "Baby Play"),
        ("pet",      "Pet Toys"),
        ("kitchen",  "Kitchen Silicone"),
    ]

    # Age group choices
    AGE_GROUP_CHOICES = [
        ("0-3", "0–3 Years"),
        ("3-7", "3–7 Years"),
        ("7+", "7+ Years"),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name          = models.CharField(max_length=255)
    description   = models.TextField()
    category      = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="educational")
    age_group     = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, default="3-7")
    
    # NEW FIELDS based on user request
    colors        = models.CharField(max_length=200, default="Pink", help_text="e.g., Pink, Blue, Green")
    mrp           = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Maximum Retail Price")
    price         = models.DecimalField(max_digits=8, decimal_places=2, help_text="Selling Price (e.g., 1089.34)")
    offer_details = models.CharField(max_length=255, null=True, blank=True, help_text="e.g., free-shipping, 50% offer from MRP")
    
    # Hidden fields used internally
    is_discount   = models.BooleanField(default=False)
    discount_price= models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    stock         = models.PositiveIntegerField(default=100) # Default to 100 so it's always in stock
    no_of_sales   = models.IntegerField(default=0)
    is_featured   = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=True)

    # Multiple product images
    image_1 = models.ImageField(upload_to="product_images/", default="default_product.jpg")
    image_2 = models.ImageField(upload_to="product_images/", null=True, blank=True)
    image_3 = models.ImageField(upload_to="product_images/", null=True, blank=True)
    image_4 = models.ImageField(upload_to="product_images/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        if not self.pk and Product.objects.count() >= 10:
            raise ValidationError("Product Limit Reached: You cannot add more than 10 products to Fimiku.")

    def __str__(self):
        return self.name

    def get_display_price(self):
        """Return the effective selling price."""
        if self.is_discount and self.discount_price:
            return self.discount_price
        return self.price

    def discount_percentage(self):
        """Calculate % off for display."""
        if self.is_discount and self.discount_price:
            return round(100 - (float(self.discount_price) / float(self.price)) * 100)
        return 0

    def get_colors_list(self):
        """Returns a list of colors from the comma-separated string."""
        if self.colors:
            return [c.strip() for c in self.colors.split(',') if c.strip()]
        return []

    def is_in_stock(self):
        return self.stock > 0

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.reviews.count()


# ─────────────────────────────────────────────
# Wishlist Model
# ─────────────────────────────────────────────
class Wishlist(models.Model):
    """Stores product wishlists per user (session or logged-in)."""
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"


# ─────────────────────────────────────────────
# Review & Rating Model
# ─────────────────────────────────────────────
class Review(models.Model):
    """Customer reviews and star ratings for products."""
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating     = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title      = models.CharField(max_length=200, blank=True)
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")  # one review per user per product

    def __str__(self):
        return f"{self.user.username} – {self.product.name} ({self.rating}★)"


# ─────────────────────────────────────────────
# Contact / Enquiry Form
# ─────────────────────────────────────────────
class CustomerForm(models.Model):
    name     = models.CharField(max_length=255)
    phone_no = models.BigIntegerField()
    email    = models.EmailField()
    subject  = models.CharField(max_length=255)
    message  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name