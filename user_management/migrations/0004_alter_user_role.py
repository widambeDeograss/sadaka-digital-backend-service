# Generated by Django 5.0.6 on 2024-10-04 10:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0003_user_is_sp_admin_user_is_sp_manager_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_role', to='user_management.systemrole'),
        ),
    ]