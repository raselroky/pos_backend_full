# Generated by Django 3.1.4 on 2025-03-01 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_csutomizemessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csutomizemessage',
            name='topics',
            field=models.CharField(blank=True, choices=[('None', 'None'), ('Sale', 'Sale'), ('Sale Return', 'Sale Return'), ('Stock Transfer', 'Stock Transfer'), ('Stock Adjustment', 'Stock Adjustment'), ('Purchase', 'Purchase'), ('Purchase Return', 'Purchase Return'), ('Valentines', 'Valentines'), ('Pohela Baishak', 'Pohela Baishak'), ('Eid', 'Eid'), ('Ramadan', 'Ramadan'), ('Special', 'Special'), ('Other', 'Other')], default='None', max_length=500, null=True),
        ),
    ]
