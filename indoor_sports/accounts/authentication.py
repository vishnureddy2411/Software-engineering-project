import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from accounts.models import Admin, User

logger = logging.getLogger(__name__)

class MultiModelBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        logger.info(f"Authenticating identifier: {username}")

        # Try Admin
        try:
            admin = Admin.objects.get(emailid=username)
            if is_password_valid(password, admin.password):
                logger.info(f"Authenticated as admin: {admin.emailid}")
                return admin
            else:
                logger.warning("Admin password mismatch.")
        except Admin.DoesNotExist:
            logger.info("Admin not found.")

        # Try User
        try:
            user = User.objects.get(username=username)
            if is_password_valid(password, user.password):
                logger.info(f"Authenticated as user: {user.username}")
                return user
            else:
                logger.warning("User password mismatch.")
        except User.DoesNotExist:
            logger.info("User not found.")

        logger.warning("Authentication failed for both admin and user.")
        return None


def is_password_valid(raw_password, stored_password):
    """
    Returns True if raw_password matches stored_password.
    Tries hash check first, falls back to plain match.
    """
    try:
        # First try hash-based check
        if check_password(raw_password, stored_password):
            return True
    except Exception:
        pass

    # Fallback: compare raw password directly (if not hashed)
    return raw_password == stored_password
