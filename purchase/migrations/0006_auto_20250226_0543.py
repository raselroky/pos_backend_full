# Generated by Django 3.1.4 on 2025-02-26 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0005_auto_20250219_0534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasereturnhistory',
            name='purchase_return',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_return_history', to='purchase.purchasereturn'),
        ),
    ]
