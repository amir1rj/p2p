# Generated by Django 5.0.6 on 2024-06-12 10:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_place_unit_alter_product_options_product_is_promoted_and_more'),
        ('vendor', '0002_alter_vendorimage_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('modify_datetime', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_delete', models.BooleanField(default=False, editable=False)),
                ('title', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('price', models.IntegerField()),
                ('is_promoted', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=1)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive', max_length=10)),
                ('is_approved', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_requests', to='product.product')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_requests', to='vendor.vendor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
