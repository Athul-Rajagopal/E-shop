# Generated by Django 4.2.3 on 2023-07-27 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_userwallet_wallet_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='discount_percent',
        ),
        migrations.AddField(
            model_name='producttable',
            name='discount_percent',
            field=models.IntegerField(default=0),
        ),
    ]
