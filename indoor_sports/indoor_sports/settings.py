import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Set to False in production

# Secret key
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# Allowed hosts
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost").split(" ")

# Installed applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django.contrib.postgres",
    "accounts",
    "bookings",
    "dashboards",
    "equipment",
    "sports",
    "login",
    "notifications",
    "payments",
    "my_referrals",
    "memberships",
    "ratings",
    "registration",
    "reports",
]

# Middleware settings
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # For static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Root URL configuration
ROOT_URLCONF = "indoor_sports.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.avatar_context",
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = "indoor_sports.wsgi.application"

# ========================== DATABASE CONFIGURATION ========================== #
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASES = {
    "default": dj_database_url.config(default=DATABASE_URL, engine="django.db.backends.postgresql")
}

# ========================== CORS SETTINGS ========================== #
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",  # Local development
    "https://software-engineering-project-tr0x.onrender.com",  # Render frontend
]

# ========================== PASSWORD VALIDATION ========================== #
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================== INTERNATIONALIZATION ========================== #
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========================== STATIC AND MEDIA FILES ========================== #
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========================== EMAIL SETTINGS ========================== #
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ========================== SESSION MANAGEMENT ========================== #
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = not DEBUG
SESSION_SAVE_EVERY_REQUEST = True

# ========================== CUSTOM USER MODEL ========================== #
AUTH_USER_MODEL = "accounts.User"

# ========================== STRIPE CONFIGURATION ========================== #
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEEKLY_PRICE = os.getenv("STRIPE_WEEKLY_PRICE", "price_weekly")
STRIPE_MONTHLY_PRICE = os.getenv("STRIPE_MONTHLY_PRICE", "price_monthly")
STRIPE_YEARLY_PRICE = os.getenv("STRIPE_YEARLY_PRICE", "price_yearly")