from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import ShippingAddress, Order, OrderItems


# ─────────────────────────────────────────────
# Inline Order Items inside Order admin
# ─────────────────────────────────────────────
class OrderItemInline(TabularInline):
    model   = OrderItems
    extra   = 0
    readonly_fields = ["product_name", "product_price", "product_qty", "line_total_display"]
    fields  = ["product", "product_name", "product_price", "product_qty", "line_total_display"]

    def line_total_display(self, obj):
        return format_html("<strong>₹{}</strong>", obj.line_total())
    line_total_display.short_description = "Line Total"


# ─────────────────────────────────────────────
# Order Admin — Premium command-center view
# ─────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display   = [
        "order_badge", "customer_display", "amount_display",
        "status_badge", "payment_badge", "ordered_date"
    ]
    list_editable  = ["status"]
    list_filter    = ["status", "is_paid", "ordered_date"]
    search_fields  = ["user__username", "user__email", "order_id"]
    readonly_fields= ["order_id", "payment_id", "signature", "ordered_date", "updated_at"]
    inlines        = [OrderItemInline]
    ordering       = ["-ordered_date"]
    list_per_page  = 25
    date_hierarchy = "ordered_date"

    fieldsets = (
        ("👤 Customer", {
            "fields": ("user", "address")
        }),
        ("💳 Payment Details", {
            "fields": ("order_id", "payment_id", "signature", "amount_paid", "is_paid")
        }),
        ("📦 Order Status", {
            "fields": ("status",)
        }),
        ("🕐 Timestamps", {
            "fields": ("ordered_date", "updated_at")
        }),
    )

    @display(description="Order #")
    def order_badge(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-weight:700;color:#7c3aed;">#{}</span>',
            str(obj.id)[:8].upper()
        )

    @display(description="Customer")
    def customer_display(self, obj):
        return format_html(
            '<div style="line-height:1.4"><strong>{}</strong><br/>'
            '<small style="color:#888;">{}</small></div>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )

    @display(description="Amount")
    def amount_display(self, obj):
        if obj.amount_paid:
            return format_html(
                '<strong style="color:#10b981;">₹{:,.0f}</strong>',
                float(obj.amount_paid)
            )
        return format_html('<span style="color:#888;">—</span>')

    @display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            "Pending":    "#f59e0b",
            "Processing": "#3b82f6",
            "Shipped":    "#8b5cf6",
            "Delivered":  "#10b981",
            "Cancelled":  "#ef4444",
        }
        color = colors.get(obj.status, "#888")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;border-radius:999px;'
            'font-size:.78rem;font-weight:700;">{}</span>',
            color, obj.status
        )

    @display(description="Paid", boolean=True)
    def payment_badge(self, obj):
        return obj.is_paid


# ─────────────────────────────────────────────
# ShippingAddress Admin
# ─────────────────────────────────────────────
@admin.register(ShippingAddress)
class ShippingAddressAdmin(ModelAdmin):
    list_display  = ["full_name", "city", "state", "pin_code", "phone_no"]
    search_fields = ["first_name", "last_name", "city", "email"]
    list_per_page = 25

    @display(description="Name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ─────────────────────────────────────────────
# OrderItems Admin
# ─────────────────────────────────────────────
@admin.register(OrderItems)
class OrderItemAdmin(ModelAdmin):
    list_display  = ["order_link", "product_name", "product_price", "product_qty", "line_total_display"]
    search_fields = ["product_name", "order__user__username"]
    list_per_page = 25

    @display(description="Order")
    def order_link(self, obj):
        return format_html(
            '<a href="/admin/payment/order/{}/change/" style="color:#7c3aed;font-weight:700;">#{}</a>',
            obj.order.id, str(obj.order.id)[:8].upper()
        )

    @display(description="Line Total")
    def line_total_display(self, obj):
        return format_html("<strong>₹{}</strong>", obj.line_total())
