# Generated by Django 5.0.6 on 2024-11-11 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0016_revenue_revenue_type_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='wahumini',
            name='type',
            field=models.CharField(default='Mtu mzima', max_length=27),
        ),
    ]
