# Generated by Django 5.0.6 on 2024-06-21 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotapp', '0011_alter_machineparameter_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machineparameter',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
