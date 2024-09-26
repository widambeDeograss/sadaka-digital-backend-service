from django.urls import path
from .views import *
app_name = 'user_management'

urlpatterns = [
    path('register-user', RegisterUser.as_view(), name="register_user"),
    path('login-user', LoginView.as_view(), name="login_user"),
    path('change-password', ChangePasswordView.as_view(), name="change_password"),
    path('activate-deactivate-staff/', ActivateDeactivateStaff.as_view(), name="activate_deactivate_staff"),
    path('delete-staff/', DeleteStaffView.as_view(), name="delete_staff"),
]
