from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            print("----------------------------------------------------------")
            print(user)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            print("Password is correct.")
            return user

        print("Password is incorrect.")
        return None
