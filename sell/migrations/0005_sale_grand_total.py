# Generated by Django 3.1.4 on 2025-03-15 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sell', '0004_auto_20250219_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='grand_total',
            field=models.FloatField(default=0),
        ),
    ]
