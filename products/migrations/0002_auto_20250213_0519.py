# Generated by Django 3.1.4 on 2025-02-13 05:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('catalog', '0002_auto_20250213_0519'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('branch', '0002_auto_20250213_0519'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariantattribute',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_productvariantattribute_created_by', related_query_name='products_productvariantattribute_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productvariantattribute',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AddField(
            model_name='productvariantattribute',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_productvariantattribute_updated_by', related_query_name='products_productvariantattribute_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productvariantattribute',
            name='variation_attribute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.attributevariation'),
        ),
        migrations.AddField(
            model_name='productbarcodes',
            name='branch',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_productbarcodes_branch', related_query_name='products_productbarcodes_branch', to='branch.branch'),
        ),
        migrations.AddField(
            model_name='productbarcodes',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_productbarcodes_created_by', related_query_name='products_productbarcodes_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productbarcodes',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AddField(
            model_name='productbarcodes',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_productbarcodes_updated_by', related_query_name='products_productbarcodes_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='branch',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_product_branch', related_query_name='products_product_branch', to='branch.branch'),
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.brand'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.category'),
        ),
        migrations.AddField(
            model_name='product',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_product_created_by', related_query_name='products_product_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.subcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.productunit'),
        ),
        migrations.AddField(
            model_name='product',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_product_updated_by', related_query_name='products_product_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['-created_at'], name='products_created_a77fb9_idx'),
        ),
    ]
