# Generated by Django 4.2.3 on 2023-07-27 14:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0021_alter_cart_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='coupon',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 27, 14, 52, 3, 611661, tzinfo=datetime.timezone.utc)),
        ),
    ]
