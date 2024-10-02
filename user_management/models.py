from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid


class SystemRole(models.Model):
    role_name = models.CharField(max_length=255, unique=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    STATUS = (
        ("DELETED", "User deleted"),
        ("ACTIVE", "Active user"),
        ("INACTIVE", "Inactive user"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    user_active = models.BooleanField(default=True)
    user_deleted = models.BooleanField(default=False)
    user_created_at = models.DateTimeField(auto_now_add=True)
    role = models.OneToOneField(SystemRole, on_delete=models.CASCADE, blank=True, null=True, related_name='custom_role')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [email]


    # Update these fields
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Unique name to avoid clashes
        blank=True,
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Unique name to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user_table'


class SystemPermission(models.Model):
    permission_name = models.CharField(max_length=255, unique=True)
    role = models.ForeignKey(SystemRole, on_delete=models.CASCADE, related_name='role_permissions')
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.permission_name


from django.db import models

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.notification_type} - {self.message[:20]}"

    def mark_as_read(self):
        """Marks the notification as read."""
        self.is_read = True
        self.save()



