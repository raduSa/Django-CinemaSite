# Generated by Django 5.1.1 on 2025-01-03 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0010_customuser_data_autentificare'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='data_autentificare',
        ),
    ]
