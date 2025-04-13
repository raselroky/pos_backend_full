# Generated by Django 3.1.4 on 2025-04-12 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_auto_20250408_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='productbarcodes',
            name='quotation_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productbarcodes',
            name='product_status',
            field=models.CharField(choices=[('Sold', 'Sold'), ('Purchased', 'Purchased'), ('Sales Return', 'Sales Return'), ('Purchase Return', 'Purchase Return'), ('Damage', 'Damage'), ('Quotation', 'Quotation')], default=None, max_length=50),
        ),
    ]
