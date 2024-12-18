# Generated by Django 5.0.6 on 2024-10-04 05:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service_providers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='wahumini',
            name='user',
            field=models.OneToOneField(blank=True, help_text='Link to a user if the wahumini is a registered user.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wahumini', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cardsnumber',
            name='mhumini',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nambaza_kadi', to='service_providers.wahumini'),
        ),
        migrations.AddField(
            model_name='ahadi',
            name='wahumini',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ahadi', to='service_providers.wahumini'),
        ),
        migrations.AddField(
            model_name='zaka',
            name='bahasha',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='service_providers.cardsnumber'),
        ),
        migrations.AddField(
            model_name='zaka',
            name='church',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_providers.serviceprovider'),
        ),
        migrations.AddField(
            model_name='zaka',
            name='payment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_providers.paymenttype'),
        ),
    ]
