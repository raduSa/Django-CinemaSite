# Generated by Django 5.1.1 on 2024-12-05 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_customuser_data_nastere_customuser_localitate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cod',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='email_confirmat',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='telefon',
            field=models.CharField(max_length=10),
        ),
    ]
