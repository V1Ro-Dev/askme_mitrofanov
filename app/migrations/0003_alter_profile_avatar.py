# Generated by Django 4.2.16 on 2024-12-04 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_answerlike_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='profile.jpg', null=True, upload_to='avatars/'),
        ),
    ]
