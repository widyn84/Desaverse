# Generated by Django 4.1.7 on 2023-12-23 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0034_likevideo_contentvideo_likes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contentvideo',
            old_name='likes',
            new_name='liked_by',
        ),
    ]