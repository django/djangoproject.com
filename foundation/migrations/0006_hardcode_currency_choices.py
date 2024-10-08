# Generated by Django 4.2.14 on 2024-09-26 11:12

from decimal import Decimal

import djmoney.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0005_alter_approvedgrant_amount_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvedgrant',
            name='amount',
            field=djmoney.models.fields.MoneyField(currency_choices=[('AUD', 'Australian Dollar'), ('EUR', 'Euro'), ('NGN', 'Nigerian Naira'), ('USD', 'US Dollar')], decimal_places=2, default=Decimal('0.0'), default_currency='USD', max_digits=10),
        ),
        migrations.AlterField(
            model_name='approvedgrant',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('AUD', 'Australian Dollar'), ('EUR', 'Euro'), ('NGN', 'Nigerian Naira'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='treasurer_balance_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3),
        ),
    ]
