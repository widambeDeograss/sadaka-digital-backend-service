# Generated by Django 5.0.6 on 2024-10-04 05:57

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_name', models.CharField(max_length=255, unique=True)),
                ('inserted_by', models.CharField(max_length=255)),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('user_active', models.BooleanField(default=True)),
                ('user_deleted', models.BooleanField(default=False)),
                ('user_created_at', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_user_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_permissions_set', to='auth.permission')),
            ],
            options={
                'db_table': 'user_table',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('success', 'Success'), ('error', 'Error')], default='info', max_length=10)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=255, unique=True)),
                ('inserted_by', models.CharField(max_length=255)),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('permissions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_permissions', to='user_management.systempermission')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_role', to='user_management.systemrole'),
        ),
    ]
