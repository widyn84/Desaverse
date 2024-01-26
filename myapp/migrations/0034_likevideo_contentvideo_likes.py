# Generated by Django 4.1.7 on 2023-12-23 11:09

from django.db import migrations, models
import django.db.models.deletion
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0033_alter_account_type_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeVideo',
            fields=[
                ('id', models.IntegerField(default=myapp.models.IntDefault, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.account')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.contentvideo')),
            ],
        ),
        migrations.AddField(
            model_name='contentvideo',
            name='likes',
            field=models.ManyToManyField(related_name='liked_videos', through='myapp.LikeVideo', to='myapp.account'),
        ),
    ]