from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from payment.models import Order, OrderItems
from .models import Product, CustomerForm, Wishlist, Review


# ─────────────────────────────────────────────
# Homepage
# ─────────────────────────────────────────────
def home(request):
    """Homepage showing featured toys, categories, and best sellers."""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    best_sellers      = Product.objects.filter(is_active=True).order_by("-no_of_sales")[:8]
    new_arrivals      = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    discounted        = Product.objects.filter(is_discount=True, is_active=True)[:4]

    # Category display with product counts
    categories = [
        {"key": "educational",    "label": "Educational",       "icon": "📚"},
        {"key": "remote_control", "label": "Remote Control",    "icon": "🚗"},
        {"key": "soft_toys",      "label": "Soft Toys",         "icon": "🧸"},
        {"key": "outdoor",        "label": "Outdoor Toys",      "icon": "⚽"},
        {"key": "puzzles",        "label": "Puzzles & Board",   "icon": "🧩"},
        {"key": "action_figures", "label": "Action Figures",    "icon": "🦸"},
    ]

    context = {
        "featured_products": featured_products,
        "best_sellers":      best_sellers,
        "new_arrivals":      new_arrivals,
        "discounted":        discounted,
        "categories":        categories,
    }
    return render(request, "index.html", context)


# ─────────────────────────────────────────────
# Products Listing with search + filter
# ─────────────────────────────────────────────
def products(request, product_cat=None):
    """Product listing with category, age-group, price filters and search."""
    all_products = Product.objects.filter(is_active=True)

    # Category filter
    category = request.GET.get("category") or product_cat
    if category:
        all_products = all_products.filter(category=category)

    # Age group filter
    age_group = request.GET.get("age_group")
    if age_group:
        all_products = all_products.filter(age_group=age_group)

    # Price filter
    max_price = request.GET.get("max_price")
    if max_price:
        try:
            all_products = all_products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Search
    search = request.GET.get("q")
    if search:
        all_products = all_products.filter(
            Q(name__icontains=search) | Q(description__icontains=search) | Q(category__icontains=search)
        )

    # Sorting
    sort = request.GET.get("sort", "-created_at")
    sort_options = {
        "price_asc":  "price",
        "price_desc": "-price",
        "popular":    "-no_of_sales",
        "newest":     "-created_at",
        "rating":     "-no_of_sales",   # fallback until annotation used
    }
    all_products = all_products.order_by(sort_options.get(sort, "-created_at"))

    paginator    = Paginator(all_products, 12)
    page         = request.GET.get("page")
    all_products = paginator.get_page(page)

    # For wishlist badge
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)
        )

    context = {
        "products":     all_products,
        "category":     category,
        "age_group":    age_group,
        "search":       search,
        "sort":         sort,
        "wishlist_ids": [str(i) for i in wishlist_ids],
        "categories": [
            ("educational",    "Educational"),
            ("remote_control", "Remote Control"),
            ("soft_toys",      "Soft Toys"),
            ("outdoor",        "Outdoor Toys"),
            ("puzzles",        "Puzzles & Board"),
            ("action_figures", "Action Figures"),
        ],
        "age_groups": [
            ("0-3", "0–3 Years"),
            ("3-7", "3–7 Years"),
            ("7+",  "7+ Years"),
        ],
    }
    return render(request, "products.html", context)


# ─────────────────────────────────────────────
# Product Detail Page
# ─────────────────────────────────────────────
def product_detail(request, id):
    """Full product detail with gallery, reviews, and related products."""
    product  = get_object_or_404(Product, id=id, is_active=True)
    reviews  = product.reviews.all().order_by("-created_at")
    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0

    # Related products (same category, excluding current)
    related  = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    # Has user already reviewed?
    user_review = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    # Handle review submission
    if request.method == "POST" and request.user.is_authenticated:
        rating  = int(request.POST.get("rating", 5))
        title   = request.POST.get("title", "")
        body    = request.POST.get("body", "")

        if user_review:
            user_review.rating = rating
            user_review.title  = title
            user_review.body   = body
            user_review.save()
            messages.success(request, "Your review has been updated!")
        else:
            Review.objects.create(
                product=product, user=request.user,
                rating=rating, title=title, body=body
            )
            messages.success(request, "Thank you for your review!")
        return redirect("product", id=product.id)

    context = {
        "product":      product,
        "reviews":      reviews,
        "avg_rating":   round(avg_rating, 1),
        "related":      related,
        "user_review":  user_review,
        "in_wishlist":  in_wishlist,
    }
    return render(request, "product.html", context)


# ─────────────────────────────────────────────
# Wishlist
# ─────────────────────────────────────────────
@login_required
def wishlist(request):
    """Display user's wishlist."""
    items = Wishlist.objects.filter(user=request.user).select_related("product")
    return render(request, "wishlist.html", {"items": items})


@login_required
def toggle_wishlist(request):
    """AJAX: add or remove product from wishlist."""
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product    = get_object_or_404(Product, id=product_id)
        obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            obj.delete()
            return JsonResponse({"status": "removed"})
        return JsonResponse({"status": "added"})
    return JsonResponse({"error": "Invalid request"}, status=400)


# ─────────────────────────────────────────────
# Orders (user view)
# ─────────────────────────────────────────────
@login_required
def your_order(request):
    """Show logged-in user's order history."""
    orders = Order.objects.filter(user=request.user, is_paid=True).order_by("-ordered_date")
    return render(request, "your_orders.html", {"orders": orders})


def order_details(request, pk):
    """Detailed view of a single order."""
    if not request.user.is_authenticated:
        return redirect("account_login")
    order    = get_object_or_404(Order, pk=pk, user=request.user)
    items    = OrderItems.objects.filter(order=order)
    context  = {"order": order, "items": items}
    return render(request, "order_details.html", context)


# ─────────────────────────────────────────────
# Admin: Order Management Dashboard
# ─────────────────────────────────────────────
def order_dashboard(request):
    """Superuser order management view."""
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect("home")

    status_filter = request.GET.get("status", "")
    orders = Order.objects.filter(is_paid=True).order_by("-ordered_date")
    if status_filter:
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 20)
    page      = request.GET.get("page")
    orders    = paginator.get_page(page)

    context = {
        "orders":        orders,
        "status_filter": status_filter,
        "status_choices": Order.STATUS_CHOICES,
    }
    return render(request, "order_dashboard.html", context)


def update_order_status(request, pk):
    """Superuser: update order status (Pending → Shipped → Delivered)."""
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect("home")
    order  = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status")
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        messages.success(request, f"Order status updated to {order.get_status_display()}.")
    return redirect("order_dashboard")


# ─────────────────────────────────────────────
# Static pages
# ─────────────────────────────────────────────
def about_us(request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        try:
            CustomerForm.objects.create(
                name     = request.POST.get("cname"),
                email    = request.POST.get("cemail"),
                phone_no = int(request.POST.get("cphone", 0)),
                subject  = request.POST.get("csubject"),
                message  = request.POST.get("cmessage"),
            )
            messages.success(request, "Your message has been sent. We'll get back to you soon!")
            return redirect("contact")
        except Exception as e:
            messages.error(request, "There was a problem submitting your form. Please try again.")

    return render(request, "contact.html")


def terms(request):
    return render(request, "terms.html")


def policy(request):
    return render(request, "privacy_policy.html")


def refund(request):
    return render(request, "refund.html")
