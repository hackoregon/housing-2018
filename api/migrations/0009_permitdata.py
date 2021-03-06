# Generated by Django 2.0.1 on 2018-05-24 03:20

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20180523_2331'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermitData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_date', models.DateTimeField()),
                ('issue_date', models.DateTimeField()),
                ('status', models.CharField(max_length=255)),
                ('year', models.PositiveSmallIntegerField()),
                ('new_class', models.CharField(max_length=255)),
                ('new_type', models.CharField(max_length=255)),
                ('neighborhood', models.CharField(max_length=255)),
                ('pdx_bnd', models.CharField(max_length=255)),
                ('is_adu', models.CharField(max_length=5)),
                ('rev', models.CharField(max_length=255)),
                ('folder_number', models.CharField(max_length=20)),
                ('property_address', models.CharField(max_length=255)),
                ('work_description', models.TextField()),
                ('sub', models.CharField(max_length=255)),
                ('occ', models.CharField(max_length=255)),
                ('new_units', models.PositiveSmallIntegerField()),
                ('folder_des', models.CharField(max_length=255)),
                ('valuation', models.DecimalField(decimal_places=2, max_digits=19)),
                ('const', models.CharField(max_length=255)),
                ('proplot', models.CharField(max_length=255)),
                ('propgisid1', models.CharField(max_length=255)),
                ('property_ro', models.CharField(max_length=255)),
                ('folder_rsn', models.IntegerField()),
                ('x_coord', models.DecimalField(decimal_places=6, max_digits=19)),
                ('y_coord', models.DecimalField(decimal_places=6, max_digits=19)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
    ]
