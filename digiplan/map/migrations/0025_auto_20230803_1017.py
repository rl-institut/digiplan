# Generated by Django 3.2.20 on 2023-08-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0024_auto_20230706_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='biomass',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='biomass',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='biomass',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='biomass',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='biomass',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='biomass',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='biomass',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='combustion',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gsgk',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='hydro',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvground',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pvroof',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='capacity_gross',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='commissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='commissioning_date_planned',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='decommissioning_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='windturbine',
            name='voltage_level',
            field=models.CharField(max_length=50, null=True),
        ),
    ]