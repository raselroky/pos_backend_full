# Generated by Django 3.1.4 on 2025-02-27 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_auto_20250225_0731'),
    ]

    operations = [
        migrations.AddField(
            model_name='productbarcodes',
            name='inv_sold',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
