# Generated by Django 4.1.7 on 2023-12-07 07:02

from django.db import migrations, models
import django.db.models.deletion
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_article_creator_article_isaccepted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='type_account',
            field=models.CharField(choices=[('S', 'Superadmin'), ('P', 'PUBLIC'), ('V', 'VERIFIKATOR'), ('C', 'CHANNEL'), ('CM', 'CHANNEL MANAGER'), ('R', 'REVIEWER')], default='P', max_length=10),
        ),
        migrations.CreateModel(
            name='ReviewVideo',
            fields=[
                ('id', models.IntegerField(default=myapp.models.IntDefault, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Menunggu Direview'), ('accepted', 'Diterima'), ('rejected', 'Ditolak')], default='pending', max_length=20)),
                ('pesan', models.TextField(blank=True, max_length=40000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('video', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review_video', to='myapp.contentvideo')),
            ],
        ),
    ]
