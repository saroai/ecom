from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from unfold.admin import ModelAdmin
from unfold.decorators import action, display
from .models import Product, Wishlist, Review, CustomerForm


# ─────────────────────────────────────────────
# Sidebar badge callbacks
# ─────────────────────────────────────────────
def pending_orders_badge(request):
    try:
        from payment.models import Order
        count = Order.objects.filter(is_paid=True, status="Pending").count()
        return str(count) if count > 0 else None
    except Exception:
        return None


def product_count_badge(request):
    try:
        count = Product.objects.filter(is_active=True, stock__lte=5).count()
        return f"{count} low" if count > 0 else None
    except Exception:
        return None


def enquiry_count_badge(request):
    try:
        count = CustomerForm.objects.count()
        return str(count) if count > 0 else None
    except Exception:
        return None


# ─────────────────────────────────────────────
# Product Admin — Rich toy management panel
# ─────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display  = [
        "product_thumbnail", "name", "colors",
        "mrp", "price", "offer_details"
    ]
    list_display_links = ["product_thumbnail", "name"]
    search_fields = ["name", "description"]
    ordering      = ["-created_at"]
    list_per_page = 25

    fieldsets = (
        ("💎 Product Details", {
            "fields": ("name", "description", "colors")
        }),
        ("💰 Pricing & Offers", {
            "fields": ("mrp", "price", "offer_details")
        }),
        ("🖼️ Product Images", {
            "fields": ("image_1", "image_2", "image_3", "image_4"),
            "classes": ("wide",)
        }),
    )

    @display(description="Preview")
    def product_thumbnail(self, obj):
        if obj.image_1:
            return format_html(
                '<img src="{}" style="width:52px;height:52px;object-fit:cover;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.18);" />',
                obj.image_1.url
            )
        return format_html('<span style="color:#888;">No img</span>')




# ─────────────────────────────────────────────
# Review Admin
# ─────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display  = ["product", "user", "rating_stars", "title", "created_at"]
    list_filter   = ["rating", "created_at"]
    search_fields = ["product__name", "user__username", "title"]
    ordering      = ["-created_at"]
    list_per_page = 25

    @display(description="Rating")
    def rating_stars(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html('<span style="color:#f59e0b;font-size:1rem;">{}</span>', stars)


# ─────────────────────────────────────────────
# Wishlist Admin
# ─────────────────────────────────────────────
@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    list_display  = ["user", "product", "added_at"]
    search_fields = ["user__username", "product__name"]
    list_per_page = 25


# ─────────────────────────────────────────────
# CustomerForm Admin
# ─────────────────────────────────────────────
@admin.register(CustomerForm)
class CustomerFormAdmin(ModelAdmin):
    list_display  = ["name", "email_link", "phone_no", "subject", "created_at"]
    search_fields = ["name", "email", "subject"]
    ordering      = ["-created_at"]
    list_per_page = 25

    @display(description="Email")
    def email_link(self, obj):
        return format_html('<a href="mailto:{}" style="color:#7c3aed;">{}</a>', obj.email, obj.email)


# ─────────────────────────────────────────────
# Customize admin site branding
# ─────────────────────────────────────────────
admin.site.site_header  = "💎 Fimiku Command Center"
admin.site.site_title   = "Fimiku Admin"
admin.site.index_title  = "Dashboard Overview"