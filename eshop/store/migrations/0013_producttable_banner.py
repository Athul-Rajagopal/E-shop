# Generated by Django 4.2.3 on 2023-07-30 05:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_banner'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttable',
            name='banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.banner'),
        ),
    ]
