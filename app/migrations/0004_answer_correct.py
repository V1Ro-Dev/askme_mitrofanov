# Generated by Django 4.2.16 on 2024-12-11 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_profile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='correct',
            field=models.BooleanField(default=False),
        ),
    ]
