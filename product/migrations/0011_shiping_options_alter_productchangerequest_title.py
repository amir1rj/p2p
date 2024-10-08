# Generated by Django 5.0.6 on 2024-06-16 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_remove_productchangerequest_information'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shiping_options',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('modify_datetime', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_delete', models.BooleanField(default=False, editable=False)),
                ('text', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='productchangerequest',
            name='title',
            field=models.CharField(max_length=60),
        ),
    ]
