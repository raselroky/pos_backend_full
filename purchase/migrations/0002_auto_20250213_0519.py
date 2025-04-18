# Generated by Django 3.1.4 on 2025-02-13 05:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0002_auto_20250213_0519'),
        ('purchase', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0002_auto_20250213_0519'),
        ('contacts', '0002_auto_20250213_0519'),
        ('branch', '0002_auto_20250213_0519'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasereturnhistory',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasereturnhistory_created_by', related_query_name='purchase_purchasereturnhistory_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchasereturnhistory',
            name='purchase_history',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_return_details', to='purchase.purchasehistory'),
        ),
        migrations.AddField(
            model_name='purchasereturnhistory',
            name='purchase_return',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_return_details', to='purchase.purchasereturn'),
        ),
        migrations.AddField(
            model_name='purchasereturnhistory',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasereturnhistory_updated_by', related_query_name='purchase_purchasereturnhistory_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchasereturn',
            name='branch',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasereturn_branch', related_query_name='purchase_purchasereturn_branch', to='branch.branch'),
        ),
        migrations.AddField(
            model_name='purchasereturn',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasereturn_created_by', related_query_name='purchase_purchasereturn_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchasereturn',
            name='purchase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_returns', to='purchase.purchase'),
        ),
        migrations.AddField(
            model_name='purchasereturn',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasereturn_updated_by', related_query_name='purchase_purchasereturn_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='branch',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasehistory_branch', related_query_name='purchase_purchasehistory_branch', to='branch.branch'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_history', to='catalog.brand'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_history', to='catalog.colorvariation'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasehistory_created_by', related_query_name='purchase_purchasehistory_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_history', to='products.product'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='purchase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_history', to='purchase.purchase'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_history', to='catalog.attributevariation'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='uom',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_history', to='catalog.productunit'),
        ),
        migrations.AddField(
            model_name='purchasehistory',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchasehistory_updated_by', related_query_name='purchase_purchasehistory_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchase',
            name='branch',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchase_branch', related_query_name='purchase_purchase_branch', to='branch.branch'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchase_created_by', related_query_name='purchase_purchase_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchase',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase', to='contacts.contact'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_purchase_updated_by', related_query_name='purchase_purchase_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='additionalexpense',
            name='branch',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_additionalexpense_branch', related_query_name='purchase_additionalexpense_branch', to='branch.branch'),
        ),
        migrations.AddField(
            model_name='additionalexpense',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_additionalexpense_created_by', related_query_name='purchase_additionalexpense_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='additionalexpense',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_additionalexpense_updated_by', related_query_name='purchase_additionalexpense_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='purchasereturnhistory',
            index=models.Index(fields=['-purchase_return', 'purchase_history', '-created_at'], name='purchase_re_purchas_c9d29c_idx'),
        ),
        migrations.AddIndex(
            model_name='purchasereturn',
            index=models.Index(fields=['-purchase', '-created_at'], name='purchase_re_purchas_7e55db_idx'),
        ),
        migrations.AddIndex(
            model_name='purchasehistory',
            index=models.Index(fields=['-product', 'purchase', '-created_at'], name='purchase_hi_product_41a27c_idx'),
        ),
        migrations.AddIndex(
            model_name='purchase',
            index=models.Index(fields=['-supplier', '-created_at'], name='purchase_supplie_150e60_idx'),
        ),
    ]
