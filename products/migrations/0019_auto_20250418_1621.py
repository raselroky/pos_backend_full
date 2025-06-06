# Generated by Django 3.1.4 on 2025-04-18 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_productbarcodes_inv_quotation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productbarcodes',
            name='product_status',
            field=models.CharField(choices=[('Select Status', 'Select Status'), ('Sold', 'Sold'), ('Purchased', 'Purchased'), ('Sales Return', 'Sales Return'), ('Purchase Return', 'Purchase Return'), ('Damage', 'Damage'), ('Quotation', 'Quotation')], default='Select Status', max_length=50),
        ),
    ]
