# Generated by Django 5.1.1 on 2025-01-04 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0011_remove_customuser_data_autentificare'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='blocat',
            field=models.BooleanField(default=False),
        ),
    ]