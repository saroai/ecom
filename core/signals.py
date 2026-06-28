from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User

@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """
    If a user logs in with Google and the email already exists in the local database,
    automatically connect the Google account to the local user account so they don't get 
    stuck on the signup page with an "Email already exists" error.
    """
    if sociallogin.is_existing:
        return

    # Check if the email provided by the social account exists in the local db
    if 'email' in sociallogin.account.extra_data:
        email = sociallogin.account.extra_data['email'].lower()
        try:
            user = User.objects.get(email__iexact=email)
            # If user exists, connect the social account to it
            sociallogin.connect(request, user)
            
            # Optionally mark the email as verified since it came from Google
            EmailAddress.objects.get_or_create(
                user=user, 
                email=email, 
                defaults={'verified': True, 'primary': True}
            )
        except User.DoesNotExist:
            pass
