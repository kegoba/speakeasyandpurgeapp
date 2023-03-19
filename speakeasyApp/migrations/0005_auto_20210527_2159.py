# Generated by Django 2.2.3 on 2021-05-27 20:59

from django.db import migrations, models
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('speakeasyApp', '0004_auto_20210527_2154'),
    ]

    operations = [
        migrations.CreateModel(
            name='Myvideo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=50)),
                ('video', s3direct.fields.S3DirectField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'videos',
                'verbose_name': 'video',
            },
        ),
        migrations.AlterModelOptions(
            name='videos',
            options={},
        ),
    ]
