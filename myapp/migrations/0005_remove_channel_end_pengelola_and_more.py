# Generated by Django 4.1.7 on 2023-11-30 04:26

from django.db import migrations, models
import django.db.models.deletion
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_channel_end_pengelola'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='end_pengelola',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='pengelola',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='start_pengelola',
        ),
        migrations.AlterField(
            model_name='article',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_article', to='myapp.channel'),
        ),
        migrations.AlterField(
            model_name='channelverification',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_verification', to='myapp.channel'),
        ),
        migrations.AlterField(
            model_name='contentvideo',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_videos', to='myapp.channel'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_galery', to='myapp.channel'),
        ),
        migrations.CreateModel(
            name='ManagerChannel',
            fields=[
                ('id', models.IntegerField(default=myapp.models.IntDefault, primary_key=True, serialize=False)),
                ('start_managing', models.DateTimeField(blank=True, null=True)),
                ('end_managing', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('account_manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='manager', to='myapp.account')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_managed', to='myapp.channel')),
            ],
        ),
    ]