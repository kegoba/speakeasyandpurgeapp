# Generated by Django 2.2.3 on 2021-06-06 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speakeasyApp', '0006_auto_20210527_0714'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='subscription_type',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
