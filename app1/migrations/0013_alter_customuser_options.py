# Generated by Django 5.1.1 on 2025-01-04 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0012_customuser_blocat'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': (('vizualizeaza_oferta', 'Vizualizeaza oferta'), ('block_user', 'Blocheaza utilizator'))},
        ),
    ]