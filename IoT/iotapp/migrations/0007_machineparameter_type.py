# Generated by Django 5.0.6 on 2024-06-21 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotapp', '0006_machinecategory_machine_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='machineparameter',
            name='type',
            field=models.CharField(choices=[('input', 'Input'), ('output', 'Output')], default='input', max_length=6),
        ),
    ]
