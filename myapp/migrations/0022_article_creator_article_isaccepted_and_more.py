# Generated by Django 4.1.7 on 2023-12-07 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_gallery_creator_gallery_isaccepted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='creator_article', to='myapp.account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='isAccepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='article',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_article', to='myapp.account'),
        ),
    ]
