# Generated by Django 5.0.6 on 2024-10-04 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_remove_systemrole_permissions_systemrole_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_sp_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_sp_manager',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_top_admin',
            field=models.BooleanField(default=False),
        ),
    ]