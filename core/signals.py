from django.dispatch import receiver
from allauth.account.signals import user_logged_in

ADMIN_EMAILS = ['fimikutoy@gmail.com', 'yakashbhai5@gmail.com']

@receiver(user_logged_in)
def manage_admin_access(request, user, **kwargs):
    """
    Automatically grant or revoke admin access based on the user's email 
    when they log in (e.g. via Google).
    """
    if user.email in ADMIN_EMAILS:
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save()
    else:
        # Revoke access if they login with any other email
        if user.is_staff or user.is_superuser:
            user.is_staff = False
            user.is_superuser = False
            user.save()
