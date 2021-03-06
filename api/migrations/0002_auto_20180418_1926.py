# Generated by Django 2.0.1 on 2018-04-18 19:26

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jchsdata',
            name='datapoint_clean',
            field=autoslug.fields.AutoSlugField(default='', editable=False, populate_from='datapoint'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jchsdata',
            name='datatype_clean',
            field=autoslug.fields.AutoSlugField(default='', editable=False, populate_from='datatype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jchsdata',
            name='valuetype_clean',
            field=autoslug.fields.AutoSlugField(default='', editable=False, populate_from='valuetype'),
            preserve_default=False,
        ),
    ]
