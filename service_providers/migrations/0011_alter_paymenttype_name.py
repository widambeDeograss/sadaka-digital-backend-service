# Generated by Django 5.0.6 on 2024-10-20 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0010_jumuiya_wahumini_jumuiya_kanda_jumuiya_kanda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttype',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]