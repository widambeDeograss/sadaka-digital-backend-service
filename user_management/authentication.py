from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            # print("----------------------------------------------------------")
            # print(user)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            print("Password is correct.")
            return user

        print("Password is incorrect.")
        return None


# class AccountExpiry:
#
# def __init__(self, get_response):
#     self.get_response = get_response
#
# def __call__(self, request):
#     current_user = request.user
#     response = self.get_response(request)
#     expiry_path = reverse('accounts:account-expired')
#
#     if current_user.is_anonymous is False:
#         if current_user.admin is False and current_user.staff is False:
#             if request.path not in [expiry_path]:
#                 expiry_date = current_user.school.account_expiry
#                 todays_date = datetime.today().date()
#
#                 if todays_date > expiry_date:
#                     return HttpResponseRedirect(expiry_path)
#     return response