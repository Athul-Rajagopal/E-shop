# Generated by Django 4.2.3 on 2023-07-30 04:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0024_alter_cart_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 30, 4, 48, 41, 999472, tzinfo=datetime.timezone.utc)),
        ),
    ]
