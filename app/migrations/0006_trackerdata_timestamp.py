# Generated by Django 5.0.6 on 2024-05-27 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_gpsdevices_token_user_device_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackerdata',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]