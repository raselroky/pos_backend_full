# Generated by Django 3.1.4 on 2025-03-20 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20250213_0525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='gender',
            field=models.CharField(choices=[('Please Select', 'Please Select'), ('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], default='Please Select', max_length=100),
        ),
    ]
