# Generated by Django 5.0.6 on 2024-10-13 18:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0006_mchango_status_alter_mchango_collected_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='ahadi',
            name='church',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='service_providers.serviceprovider'),
            preserve_default=False,
        ),
    ]
