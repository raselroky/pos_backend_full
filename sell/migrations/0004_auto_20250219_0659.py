# Generated by Django 3.1.4 on 2025-02-19 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sell', '0003_salehistory_selling_price'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='salehistory',
            name='sale_histor_product_b53178_idx',
        ),
        migrations.RenameField(
            model_name='salehistory',
            old_name='product',
            new_name='product_variant',
        ),
        migrations.AddIndex(
            model_name='salehistory',
            index=models.Index(fields=['-product_variant', 'sale', '-created_at'], name='sale_histor_product_7002e6_idx'),
        ),
    ]
