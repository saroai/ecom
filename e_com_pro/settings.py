"""
Django settings for e_com_pro project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = 'django-insecure-testkey-1234567890abcdefg'
DEBUG = True

if os.environ.get("ENVIRONMENT") == "production":
    ALLOWED_HOSTS = ["learnmythos.app", "www.learnmythos.app", "143.110.182.223"]
    CSRF_TRUSTED_ORIGINS = ["https://learnmythos.app", "https://www.learnmythos.app"]
    DEBUG = False
else:
    ALLOWED_HOSTS = ["learnmythos.app", "143.110.182.223", "localhost", "127.0.0.1"]


INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'cart.apps.CartConfig',
    "payment.apps.PaymentConfig",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    "crispy_bootstrap5",
    "django_cleanup.apps.CleanupConfig",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

ROOT_URLCONF = 'e_com_pro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "cart.context_processor.cart"
            ],
        },
    },
]

WSGI_APPLICATION = 'e_com_pro.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

if os.environ.get('production', False):
    MEDIA_ROOT = "/app/media"
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_REDIRECT_URL = "home"
ACCOUNT_SIGNUP_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "account_login"

RAZOR_PAY_SECRET_KEY = os.environ.get("RAZORPAY_SECRET_KEY", "")
RAZOR_PAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZOR_PAY_CALLBACK_URL = "payment_verify"

if os.environ.get("ENVIRONMENT") == 'production':
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

# ─────────────────────────────────────────────
# UNFOLD ADMIN PANEL SETTINGS
# ─────────────────────────────────────────────
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE":  "Fimiku Command Center",
    "SITE_HEADER": "Fimiku",
    "SITE_URL":    "/",
    "COLORS": {
        "primary": {
            "50":  "245 243 255",
            "100": "237 233 254",
            "200": "221 214 254",
            "300": "196 181 253",
            "400": "167 139 250",
            "500": "139 92 246",
            "600": "124 58 237",
            "700": "109 40 217",
            "800": "91 33 182",
            "900": "76 29 149",
            "950": "46 16 101",
        },
    },
    "SIDEBAR": {
        "show_search":           True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "items": [
                    {"title": "Overview",        "icon": "dashboard",    "link": reverse_lazy("admin:index")},
                    {"title": "Order Dashboard", "icon": "receipt_long", "link": reverse_lazy("order_dashboard")},
                ],
            },
            {
                "title": "Store",
                "separator": True,
                "items": [
                    {"title": "Products",  "icon": "inventory_2", "link": reverse_lazy("admin:core_product_changelist")},
                    {"title": "Reviews",   "icon": "star",        "link": reverse_lazy("admin:core_review_changelist")},
                    {"title": "Wishlists", "icon": "favorite",    "link": reverse_lazy("admin:core_wishlist_changelist")},
                ],
            },
            {
                "title": "Sales",
                "separator": True,
                "items": [
                    {"title": "All Orders",          "icon": "shopping_cart",  "link": reverse_lazy("admin:payment_order_changelist")},
                    {"title": "Order Items",          "icon": "list_alt",       "link": reverse_lazy("admin:payment_orderitems_changelist")},
                    {"title": "Shipping Addresses",   "icon": "local_shipping", "link": reverse_lazy("admin:payment_shippingaddress_changelist")},
                ],
            },
            {
                "title": "Customers",
                "separator": True,
                "items": [
                    {"title": "Users",     "icon": "group", "link": reverse_lazy("admin:auth_user_changelist")},
                    {"title": "Enquiries", "icon": "mail",  "link": reverse_lazy("admin:core_customerform_changelist")},
                ],
            },
        ],
    },
}

# ─────────────────────────────────────────────
# Email Configuration
# ─────────────────────────────────────────────
if os.environ.get("ENVIRONMENT") == "production":
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", EMAIL_HOST_USER)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST_USER = 'local@fimiku.com'
    ADMIN_EMAIL = 'admin@fimiku.com'