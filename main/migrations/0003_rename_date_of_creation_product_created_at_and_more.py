# Generated by Django 5.0.4 on 2024-04-22 07:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_category_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='date_of_creation',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='date_of_last_change',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.category'),
        ),
    ]
