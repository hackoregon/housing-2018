from django.db import models
from django.contrib.postgres.fields import ArrayField
from autoslug import AutoSlugField

class JCHSData(models.Model):
    datapoint = models.CharField(max_length=255, help_text='Location of data')
    source = models.CharField(max_length=4, help_text='Sheet of State of Housing Report appendix Excel file that this data comes from')
    datatype = models.CharField(max_length=255, help_text='Description of the data this value represents')
    valuetype = models.CharField(max_length=255, help_text='Type of data this value represents')
    date = models.DateField(help_text='Date of this value, if representative of an entire year the value will be on Jan 1')
    value = models.DecimalField(max_digits=24, decimal_places=5)

    # URL-friendly values to access via GET requests
    datapoint_clean = AutoSlugField(populate_from='datapoint', max_length=100)
    datatype_clean = AutoSlugField(populate_from='datatype', max_length=100)
    valuetype_clean = AutoSlugField(populate_from='valuetype', max_length=100)

class HudPitData(models.Model):
    datapoint = models.CharField(max_length=255, help_text='Location of data')
    geography = models.CharField(max_length=255, help_text='Location type')
    datatype = models.CharField(max_length=255, help_text='Description of the data this value represents')
    year = models.PositiveSmallIntegerField(help_text='Year of count')
    value = models.DecimalField(max_digits=18, decimal_places=2)

    # URL-friendly values to access via GET requests
    datapoint_clean = AutoSlugField(populate_from='datapoint', max_length=100)
    datatype_clean = AutoSlugField(populate_from='datatype', max_length=100)

class HudHicData(models.Model):
    datapoint = models.CharField(max_length=255, help_text='Location of data')
    geography = models.CharField(max_length=255, help_text='Location type')
    datatype = models.CharField(max_length=255, help_text='Description of the data this value represents')
    shelter_status = ArrayField(
        models.CharField(max_length=255, help_text='Type of shelter this value represents')
    )
    year = models.PositiveSmallIntegerField(help_text='Year of count')
    value = models.DecimalField(max_digits=18, decimal_places=2)
    
    # URL-friendly values to access via GET requests
    datapoint_clean = AutoSlugField(populate_from='datapoint', max_length=100)
    datatype_clean = AutoSlugField(populate_from='datatype', max_length=100)
    
