# Generated by Django 5.0.6 on 2024-06-16 07:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_order_shipping_option'),
        ('product', '0013_remove_product_shipping_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='product.shipping_options'),
        ),
    ]
