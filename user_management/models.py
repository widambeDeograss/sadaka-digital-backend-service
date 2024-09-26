from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [email]

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user_table'
