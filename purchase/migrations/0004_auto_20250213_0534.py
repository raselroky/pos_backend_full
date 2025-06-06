# Generated by Django 3.1.4 on 2025-02-13 05:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_auto_20250213_0525'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchase',
            options={'ordering': ['-created_at'], 'verbose_name': 'Purchase', 'verbose_name_plural': 'Purchase'},
        ),
        migrations.AlterModelOptions(
            name='purchasehistory',
            options={'ordering': ['-created_at'], 'verbose_name': 'Purchase', 'verbose_name_plural': 'Purchase Histories'},
        ),
        migrations.AlterModelOptions(
            name='purchasereturn',
            options={'ordering': ['-created_at'], 'verbose_name': 'Purchase Return', 'verbose_name_plural': 'Purchase Returns'},
        ),
        migrations.AlterModelOptions(
            name='purchasereturnhistory',
            options={'ordering': ['-created_at'], 'verbose_name': 'Purchase Return History', 'verbose_name_plural': 'Purchase Return Histories'},
        ),
    ]
