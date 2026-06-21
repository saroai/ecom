import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_com_pro.settings')
django.setup()

from core.models import Product, Review, Wishlist, CustomerForm
from payment.models import Order, OrderItems, ShippingAddress
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount, SocialToken

def clear_all_test_data():
    print("🧹 Starting cleanup of test data...")

    # 1. Payment & Cart (Delete these first to avoid foreign key issues)
    print("Deleting Order Items...")
    OrderItems.objects.all().delete()
    print("Deleting Orders...")
    Order.objects.all().delete()
    print("Deleting Shipping Addresses...")
    ShippingAddress.objects.all().delete()

    # 2. Store Models
    print("Deleting Reviews...")
    Review.objects.all().delete()
    print("Deleting Wishlists...")
    Wishlist.objects.all().delete()
    
    # Deleting Products will also automatically delete their uploaded images 
    # from the media folder because we use django-cleanup!
    print("Deleting Products and their uploaded images...")
    Product.objects.all().delete()

    # 3. CRM & Enquiries
    print("Deleting Customer Enquiries...")
    CustomerForm.objects.all().delete()

    # 4. Auth & Users (Delete all normal users and their social logins)
    print("Deleting test Social Accounts...")
    SocialToken.objects.all().delete()
    SocialAccount.objects.all().delete()
    
    print("Deleting normal test users (keeping Superusers safe)...")
    deleted_count, _ = User.objects.filter(is_staff=False, is_superuser=False).delete()
    print(f"Deleted {deleted_count} normal user accounts.")

    print("\n✅ SUCCESS! All test data has been permanently deleted.")
    print("Your database is now neat, clean, and ready for Production!")

if __name__ == "__main__":
    confirm = input("⚠️ WARNING: This will delete ALL products, orders, and normal users! Are you sure? (type 'yes' to confirm): ")
    if confirm.strip().lower() == 'yes':
        clear_all_test_data()
    else:
        print("Cleanup aborted.")
