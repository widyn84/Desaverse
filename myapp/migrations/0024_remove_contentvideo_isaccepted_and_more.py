# Generated by Django 4.1.7 on 2023-12-07 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0023_alter_account_type_account_reviewvideo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contentvideo',
            name='isAccepted',
        ),
        migrations.AddField(
            model_name='contentvideo',
            name='pesan_status',
            field=models.TextField(blank=True, max_length=40000, null=True),
        ),
        migrations.AddField(
            model_name='contentvideo',
            name='status',
            field=models.CharField(choices=[('pending', 'Menunggu Direview'), ('accepted', 'Diterima'), ('rejected', 'Ditolak')], default='pending', max_length=20),
        ),
        migrations.DeleteModel(
            name='ReviewVideo',
        ),
    ]
