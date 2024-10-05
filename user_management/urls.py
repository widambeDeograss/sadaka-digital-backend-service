from django.urls import path
from .views import *
app_name = 'user_management'

urlpatterns = [
    path('register-user', RegisterUser.as_view(), name="register_user"),
    path('login-user', LoginView.as_view(), name="login_user"),
    path('users', GetUsersView.as_view(), name="users"),
    path('change-password', ChangePasswordView.as_view(), name="change_password"),
    path('activate-deactivate-staff/', ActivateDeactivateStaff.as_view(), name="activate_deactivate_staff"),
    path('delete-staff/', DeleteStaffView.as_view(), name="delete_staff"),
    path('system-role-list-create', SystemRoleListCreateView.as_view(), name="system_role_list_create"),
    path('system-role-retrieve-update-destroy/<int:pk>', SystemRoleRetrieveUpdateDestroyView.as_view(), name="system_role_retrieve_update_destroy"),
    path('system-permission-list-create', SystemPermissionListCreateView.as_view(), name="system_permission_list_create"),
    path('system-permission-retrieve-update-destroy/<int:pk>', SystemPermissionRetrieveUpdateDestroyView.as_view(), name="system_permission_retrieve_update_destroy"),
    path('notification-list-create', NotificationListCreateView.as_view(), name="notification_list_create"),
    path('notification-retrieve-update-destroy/<int:pk>', NotificationRetrieveUpdateDestroyView.as_view(), name="notification_retrieve_update_destroy"),
]
