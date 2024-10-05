from django.contrib import admin
from .models import SystemPermission, User, Notification, SystemRole

# Register all models
admin.site.register(SystemPermission)
admin.site.register(User)
admin.site.register(Notification)
admin.site.register(SystemRole)
