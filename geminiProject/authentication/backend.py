from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()

class CustomUserAuthenticationBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user= User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None