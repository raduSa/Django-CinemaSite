# Generated by Django 5.1.1 on 2025-01-05 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0014_difuzare_nr_locuri'),
    ]

    operations = [
        migrations.AddField(
            model_name='difuzare',
            name='pret_bilet',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
    ]
