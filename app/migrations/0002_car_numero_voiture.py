# Generated by Django 4.2.8 on 2024-04-09 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='numero_voiture',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
