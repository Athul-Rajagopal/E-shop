# Generated by Django 4.2.3 on 2023-07-25 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_userwallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userwallet',
            name='wallet_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
