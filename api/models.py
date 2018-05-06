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
    
class UrbanInstituteRentalCrisisData(models.Model):
    year = models.PositiveSmallIntegerField(help_text='Year of data')
    eli_limit = models.DecimalField(max_digits=9, decimal_places=2, help_text='HUD ELI limit for family of four in the county')
    county_fips = models.CharField(max_length=10, help_text='County FIPS code')
    county_name = models.CharField(max_length=255, help_text='County name')
    state_name = models.CharField(max_length=255, help_text='State name')
    is_state_data = models.BooleanField()
    eli_renters = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of ELI renters in the county')
    aaa_units = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of affordable, adequate, and available units in the county')
    noasst_units = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of units paying less than 30% of income on rent and utilities, excluding units with project-based rental assistance')
    hud_units = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of units subsidized by HUD rental assistance, excluding units that were affordable before assistance')
    usda_units = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of units subsidized by USDA rental assistance. Imputed for 2000 data.')
    no_hud_units = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of affordable, adequate, and available units without HUD rental assistance')
    no_usda_units = models.DecimalField(max_digits=11, decimal_places=2, help_text='Number of affordable, adequate, and available units without USDA rental assistance')


    def aaa_units_per_100(self):
        return aaa_units / eli_renters * 100

    def noasst_units_per_100(self):
        return noasst_units / eli_renters * 100

    def hud_units_per_100(self):
        return hud_units / eli_renters * 100

    def usda_units_per_100(self):
        return usda_units / eli_renters * 100

    def no_hud_units_per_100(self):
        return no_hud_units / eli_renters * 100

    def no_usda_units_per_100(self):
        return no_usda_units / eli_renters * 100

