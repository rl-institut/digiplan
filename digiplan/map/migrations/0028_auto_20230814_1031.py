# Generated by Django 3.2.20 on 2023-08-14 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0027_auto_20230814_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biomass',
            name='fuel',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='biomass',
            name='technology',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
