# Generated by Django 5.0.6 on 2024-06-10 10:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_temppassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temppassword',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tmp_passwords', to=settings.AUTH_USER_MODEL),
        ),
    ]
