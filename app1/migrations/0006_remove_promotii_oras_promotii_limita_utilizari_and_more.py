# Generated by Django 5.1.1 on 2024-12-09 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0005_categorie_film_categorii_promotii'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotii',
            name='oras',
        ),
        migrations.AddField(
            model_name='promotii',
            name='limita_utilizari',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='promotii',
            name='discount',
            field=models.IntegerField(default=0),
        ),
    ]