# Generated by Django 4.2.3 on 2023-07-11 09:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0003_categorytable_is_active_productvariant_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('area', models.TextField()),
                ('house_name', models.TextField()),
                ('city', models.CharField()),
                ('pincode', models.CharField()),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.state')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
