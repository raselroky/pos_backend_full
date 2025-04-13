# Generated by Django 3.1.4 on 2025-04-12 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0006_auto_20250226_0543'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='discount_type',
            field=models.CharField(choices=[('Select Type', 'Select Type'), ('Percentage', 'Percentage'), ('Flat', 'Flat')], default='Select Type', max_length=100),
        ),
        migrations.AddField(
            model_name='purchase',
            name='payment_method',
            field=models.CharField(choices=[('Select Payment Method', 'Select Payment Method'), ('Cash', 'Cash'), ('Check', 'Check'), ('Bank-Card', 'Bank-Card'), ('Bkash', 'Bkash'), ('Nagad', 'Nagad'), ('Upay', 'Upay')], default='Select Payment Method', max_length=100),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='discount_type',
            field=models.CharField(choices=[('Select Type', 'Select Type'), ('Percentage', 'Percentage'), ('Flat', 'Flat')], default='Select Type', max_length=100),
        ),
    ]
