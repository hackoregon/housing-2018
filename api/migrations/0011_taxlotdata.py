# Generated by Django 2.0.1 on 2018-06-04 18:21

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20180524_0321'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxlotData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.FloatField()),
                ('tlid', models.CharField(max_length=16)),
                ('rno', models.CharField(max_length=10)),
                ('owner_address', models.CharField(max_length=35)),
                ('owner_city', models.CharField(max_length=30)),
                ('owner_state', models.CharField(max_length=2)),
                ('owner_zip', models.CharField(max_length=10)),
                ('site_str_no', models.IntegerField()),
                ('site_address', models.CharField(max_length=35)),
                ('site_city', models.CharField(max_length=30)),
                ('site_zip', models.CharField(max_length=10)),
                ('land_value', models.IntegerField()),
                ('building_value', models.IntegerField()),
                ('total_value', models.IntegerField()),
                ('building_sqft', models.IntegerField()),
                ('a_t_acres', models.FloatField()),
                ('year_built', models.PositiveSmallIntegerField()),
                ('prop_code', models.CharField(max_length=3)),
                ('land_use', models.CharField(max_length=3)),
                ('tax_code', models.CharField(max_length=7)),
                ('sale_date', models.DateField()),
                ('sale_price', models.IntegerField()),
                ('county', models.CharField(max_length=1)),
                ('x_coord', models.IntegerField()),
                ('y_coord', models.IntegerField()),
                ('juris_city', models.CharField(max_length=30)),
                ('gis_acres', models.FloatField()),
                ('state_class', models.CharField(max_length=4)),
                ('or_tax_lot', models.CharField(max_length=29)),
                ('orig_ogr_f', models.IntegerField()),
                ('building_value_2011', models.IntegerField()),
                ('land_value_2011', models.IntegerField()),
                ('total_value_2011', models.IntegerField()),
                ('percent_change_2011_2017', models.FloatField()),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
    ]
