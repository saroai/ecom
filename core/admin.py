from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Product, Wishlist, Review, CustomerForm


# ─────────────────────────────────────────────
# Product Admin — Rich toy management panel
# ─────────────────────────────────────────────
class ProductAdmin(ModelAdmin):
    list_display  = [
        "product_thumbnail", "name", "category", "age_group",
        "price", "discount_price", "is_discount", "stock",
        "no_of_sales", "is_featured", "is_active"
    ]
    list_display_links = ["product_thumbnail", "name"]
    list_editable = ["is_discount", "is_featured", "is_active", "stock"]
    list_filter   = ["category", "age_group", "is_discount", "is_featured", "is_active"]
    search_fields = ["name", "description", "category"]
    ordering      = ["-created_at"]
    list_per_page = 20

    fieldsets = (
        ("🧸 Basic Info", {
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

    def product_thumbnail(self, obj):
        """Show product image preview directly in admin list."""
        if obj.image_1:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:cover;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.15);" />',
                obj.image_1.url
            )
        return "No Image"
    product_thumbnail.short_description = "Preview"


# ─────────────────────────────────────────────
# Review Admin
# ─────────────────────────────────────────────
class ReviewAdmin(ModelAdmin):
    list_display  = ["product", "user", "rating", "title", "created_at"]
    list_filter   = ["rating", "created_at"]
    search_fields = ["product__name", "user__username", "title"]
    ordering      = ["-created_at"]


# ─────────────────────────────────────────────
# Wishlist Admin
# ─────────────────────────────────────────────
class WishlistAdmin(ModelAdmin):
    list_display  = ["user", "product", "added_at"]
    search_fields = ["user__username", "product__name"]


# ─────────────────────────────────────────────
# CustomerForm Admin
# ─────────────────────────────────────────────
class CustomerFormAdmin(ModelAdmin):
    list_display  = ["name", "email", "phone_no", "subject", "created_at"]
    search_fields = ["name", "email", "subject"]
    ordering      = ["-created_at"]


# Register all models
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(CustomerForm, CustomerFormAdmin)

# ─────────────────────────────────────────────
# Customize admin site branding
# ─────────────────────────────────────────────
admin.site.site_header  = "🧸 ToyZone Admin"
admin.site.site_title   = "ToyZone Admin Panel"
admin.site.index_title  = "Welcome to ToyZone Dashboard"