# Generated by Django 4.2.3 on 2023-07-27 04:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0015_alter_cart_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 27, 4, 46, 33, 779615, tzinfo=datetime.timezone.utc)),
        ),
    ]