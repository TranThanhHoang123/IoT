# Generated by Django 5.0.6 on 2024-06-20 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='address',
            field=models.CharField(blank=True, max_length=180, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
