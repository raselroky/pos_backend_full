# Generated by Django 3.1.4 on 2025-02-13 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('branch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('business_name', models.CharField(blank=True, max_length=1000, null=True)),
                ('owner_name', models.CharField(blank=True, max_length=1000, null=True)),
                ('contactor_type', models.CharField(choices=[('Please Select', 'Please Select'), ('Suppliers', 'Suppliers'), ('Customers', 'Customers'), ('Both', 'Both')], default='Please Select', max_length=1000)),
                ('business_type', models.CharField(choices=[('Please Select', 'Please Select'), ('Individual/Personal', 'Individual/Personal'), ('Business/Group', 'Business/Group')], default='Please Select', max_length=1000)),
                ('conact_id', models.CharField(blank=True, max_length=5000, null=True)),
                ('mobile', models.CharField(blank=True, max_length=1000, null=True)),
                ('mobile2', models.CharField(blank=True, max_length=1000, null=True)),
                ('email', models.CharField(blank=True, max_length=1000, null=True)),
                ('file_image', models.ImageField(blank=True, null=True, upload_to='profile_pic/')),
                ('tax_number', models.TextField(blank=True, null=True)),
                ('opening_balance', models.FloatField(default=0)),
                ('pay_term_amount', models.FloatField(default=0)),
                ('pay_term_types', models.CharField(choices=[('Please Select', 'Please Select'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Please Select', max_length=1000)),
                ('address', models.TextField(blank=True, help_text='area, city, state or zone, country, zip code', null=True)),
                ('shipping_address', models.TextField(blank=True, null=True)),
                ('sales_commission', models.TextField(blank=True, null=True)),
                ('branch', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts_contact_branch', related_query_name='contacts_contact_branch', to='branch.branch')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'db_table': 'contacts',
                'ordering': ['-id'],
            },
        ),
    ]
