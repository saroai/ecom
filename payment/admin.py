from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import ShippingAddress, Order, OrderItems


# ─────────────────────────────────────────────
# Inline Order Items inside Order admin
# ─────────────────────────────────────────────
class OrderItemInline(TabularInline):
    model   = OrderItems
    extra   = 0
    readonly_fields = ["product_name", "product_price", "product_qty", "line_total"]
    fields  = ["product", "product_name", "product_price", "product_qty", "line_total"]

    def line_total(self, obj):
        return f"₹{obj.line_total()}"
    line_total.short_description = "Line Total"


# ─────────────────────────────────────────────
# Order Admin — Full order management dashboard
# ─────────────────────────────────────────────
class OrderAdmin(ModelAdmin):
    list_display   = [
        "short_id", "user", "amount_display", "status",
        "is_paid", "ordered_date", "updated_at"
    ]
    list_editable  = ["status"]          # admin can update status directly from list
    list_filter    = ["status", "is_paid", "ordered_date"]
    search_fields  = ["user__username", "user__email", "order_id"]
    readonly_fields= ["order_id", "payment_id", "signature", "ordered_date", "updated_at"]
    inlines        = [OrderItemInline]
    ordering       = ["-ordered_date"]
    list_per_page  = 25

    fieldsets = (
        ("👤 Customer", {
            "fields": ("user", "address")
        }),
        ("💳 Payment Details", {
            "fields": ("order_id", "payment_id", "signature", "amount_paid", "is_paid")
        }),
        ("📦 Status", {
            "fields": ("status",)
        }),
        ("🕐 Timestamps", {
            "fields": ("ordered_date", "updated_at")
        }),
    )

    def short_id(self, obj):
        return str(obj.id)[:8].upper()
    short_id.short_description = "Order ID"

    def amount_display(self, obj):
        if obj.amount_paid:
            return format_html("<strong>₹{}</strong>", obj.amount_paid)
        return "—"
    amount_display.short_description = "Amount"


# ─────────────────────────────────────────────
# ShippingAddress Admin
# ─────────────────────────────────────────────
class ShippingAddressAdmin(ModelAdmin):
    list_display  = ["first_name", "last_name", "city", "state", "pin_code", "phone_no"]
    search_fields = ["first_name", "last_name", "city", "email"]


# ─────────────────────────────────────────────
# OrderItems Admin
# ─────────────────────────────────────────────
class OrderItemAdmin(ModelAdmin):
    list_display  = ["order", "product_name", "product_price", "product_qty"]
    search_fields = ["product_name", "order__user__username"]


# Register
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems, OrderItemAdmin)
