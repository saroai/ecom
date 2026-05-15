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
        "product_thumbnail", "name", "category", "age_group",
        "price", "discount_price", "is_discount", "stock_display",
        "no_of_sales", "is_featured", "is_active"
    ]
    list_display_links = ["product_thumbnail", "name"]
    list_editable = ["is_discount", "is_featured", "is_active"]
    list_filter   = ["category", "age_group", "is_discount", "is_featured", "is_active"]
    search_fields = ["name", "description", "category"]
    ordering      = ["-created_at"]
    list_per_page = 25

    fieldsets = (
        ("💎 Basic Info", {
            "fields": ("name", "description", "category", "age_group", "is_featured", "is_active")
        }),
        ("💰 Pricing & Stock", {
            "fields": ("price", "is_discount", "discount_price", "stock")
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

    @display(description="Stock", ordering="stock")
    def stock_display(self, obj):
        color = "#ef4444" if obj.stock <= 5 else "#10b981" if obj.stock > 20 else "#f59e0b"
        label = "Low" if obj.stock <= 5 else "OK"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:999px;font-size:.75rem;font-weight:700;">{} ({})</span>',
            color, label, obj.stock
        )


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