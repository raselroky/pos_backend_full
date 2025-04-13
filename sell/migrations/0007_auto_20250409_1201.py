# Generated by Django 3.1.4 on 2025-04-09 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sell', '0006_auto_20250409_1200'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'ordering': ['-created_at'], 'verbose_name': 'Sale', 'verbose_name_plural': 'Sale'},
        ),
        migrations.RemoveIndex(
            model_name='sale',
            name='sale_custome_26eb98_idx',
        ),
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['-customer', '-created_at'], name='sale_custome_96f3f0_idx'),
        ),
    ]
