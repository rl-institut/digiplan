# Generated by Django 3.2.16 on 2023-02-20 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0012_population'),
    ]

    operations = [
        migrations.AlterField(
            model_name='population',
            name='value',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
