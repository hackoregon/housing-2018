from django.db import models

class JCHSData(models.Model):
    datapoint = models.CharField(max_length=255, help_text='Location of data')
    source = models.CharField(max_length=4, help_text='Sheet of State of Housing Report appendix Excel file that this data comes from')
    datatype = models.CharField(max_length=255, help_text='Description of the data this value represents')
    valuetype = models.CharField(max_length=255, help_text='Type of data this value represents')
    date = models.DateField(help_text='Date of this value, if representative of an entire year the value will be on Jan 1')
    value = models.DecimalField(max_digits=24, decimal_places=5)
