# Generated by Django 4.2.3 on 2023-07-11 09:45

from django.db import migrations
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_state_useraddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='phone',
            field=phone_field.models.PhoneField(blank=True, max_length=31),
        ),
    ]
