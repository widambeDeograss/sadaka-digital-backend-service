# Generated by Django 5.0.6 on 2024-11-27 19:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0019_alter_cardsnumber_card_no_sadakatypes_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mavuno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('year_target_amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('collected_amount', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('status', models.BooleanField(default=True)),
                ('inserted_by', models.CharField(max_length=255)),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='MavunoPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('inserted_by', models.CharField(max_length=255)),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='ahadi',
            index=models.Index(fields=['wahumini', 'church'], name='service_pro_wahumin_4e026a_idx'),
        ),
        migrations.AddIndex(
            model_name='ahadipayments',
            index=models.Index(fields=['ahadi'], name='service_pro_ahadi_i_b33893_idx'),
        ),
        migrations.AddIndex(
            model_name='cardsnumber',
            index=models.Index(fields=['mhumini', 'card_no', 'bahasha_type'], name='service_pro_mhumini_6dd26f_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['church', 'expense_category'], name='service_pro_church__167370_idx'),
        ),
        migrations.AddIndex(
            model_name='expensecategory',
            index=models.Index(fields=['church'], name='service_pro_church__1645b3_idx'),
        ),
        migrations.AddIndex(
            model_name='jumuiya',
            index=models.Index(fields=['church', 'name'], name='service_pro_church__677654_idx'),
        ),
        migrations.AddIndex(
            model_name='kanda',
            index=models.Index(fields=['church', 'name'], name='service_pro_church__96a27f_idx'),
        ),
        migrations.AddIndex(
            model_name='mchango',
            index=models.Index(fields=['church', 'status'], name='service_pro_church__832d42_idx'),
        ),
        migrations.AddIndex(
            model_name='mchangopayments',
            index=models.Index(fields=['mchango', 'mhumini'], name='service_pro_mchango_5ab102_idx'),
        ),
        migrations.AddIndex(
            model_name='paymenttypetransfer',
            index=models.Index(fields=['church', 'transfer_date'], name='service_pro_church__698f6c_idx'),
        ),
        migrations.AddIndex(
            model_name='revenue',
            index=models.Index(fields=['church', 'date_received'], name='service_pro_church__c26f28_idx'),
        ),
        migrations.AddIndex(
            model_name='sadaka',
            index=models.Index(fields=['church', 'bahasha', 'sadaka_type'], name='service_pro_church__df2288_idx'),
        ),
        migrations.AddIndex(
            model_name='wahumini',
            index=models.Index(fields=['church', 'jumuiya', 'phone_number'], name='service_pro_church__0ce3c2_idx'),
        ),
        migrations.AddIndex(
            model_name='zaka',
            index=models.Index(fields=['church', 'bahasha', 'payment_type'], name='service_pro_church__bdf988_idx'),
        ),
        migrations.AddField(
            model_name='mavuno',
            name='church',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_providers.serviceprovider'),
        ),
        migrations.AddField(
            model_name='mavuno',
            name='jumuiya',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='service_providers.jumuiya'),
        ),
        migrations.AddField(
            model_name='mavunopayments',
            name='mavuno',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_providers.mavuno'),
        ),
        migrations.AddField(
            model_name='mavunopayments',
            name='mhumini',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='service_providers.wahumini'),
        ),
        migrations.AddField(
            model_name='mavunopayments',
            name='payment_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='service_providers.paymenttype'),
        ),
        migrations.AddIndex(
            model_name='mavuno',
            index=models.Index(fields=['jumuiya', 'church'], name='service_pro_jumuiya_e91398_idx'),
        ),
        migrations.AddIndex(
            model_name='mavunopayments',
            index=models.Index(fields=['mavuno', 'payment_type'], name='service_pro_mavuno__5497e4_idx'),
        ),
    ]