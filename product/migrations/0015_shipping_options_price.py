# Generated by Django 5.0.6 on 2024-06-19 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_remove_shipping_options_create_datetime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping_options',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
