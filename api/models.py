from django.db.models.functions import Rank
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from autoslug import AutoSlugField

class JCHSDataManager(models.Manager):
    def with_rank(self):
        ranked = JCHSData.objects.exclude(datapoint='United States').annotate(
            asc_rank=models.Window(expression=Rank(), partition_by=[models.F('datatype'),models.F('source'),models.F('date')], order_by=models.F('value').asc()),
            desc_rank=models.Window(expression=Rank(), partition_by=[models.F('datatype'),models.F('source'),models.F('date')], order_by=models.F('value').desc()),
            total=models.Window(expression=models.Count(['datatype','source','date']), partition_by=[models.F('datatype'),models.F('source'),models.F('date')])
        )
        return ranked

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

    objects = JCHSDataManager()

class HudPitDataManager(models.Manager):
    def with_rank(self):
        ranked = HudPitData.objects.annotate(
            rank=models.Window(expression=Rank(), partition_by=[models.F('datatype'),models.F('geography'),models.F('year')], order_by=models.F('value').asc()),
            total=models.Window(expression=models.Count(['datatype','geography','year']), partition_by=[models.F('datatype'),models.F('geography'),models.F('year')])
        )
        return ranked

class HudPitData(models.Model):
    datapoint = models.CharField(max_length=255, help_text='Location of data')
    geography = models.CharField(max_length=255, help_text='Location type')
    datatype = models.CharField(max_length=255, help_text='Description of the data this value represents')
    year = models.PositiveSmallIntegerField(help_text='Year of count')
    value = models.DecimalField(max_digits=18, decimal_places=2)

    # URL-friendly values to access via GET requests
    datapoint_clean = AutoSlugField(populate_from='datapoint', max_length=100)
    datatype_clean = AutoSlugField(populate_from='datatype', max_length=100)

    objects = HudPitDataManager()

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

class UrbanInstituteRentalCrisisManager(models.Manager):
    def with_rank(self):
        ranked = UrbanInstituteRentalCrisisData.objects.annotate(
            rank=models.Window(expression=Rank(), partition_by=[models.F('year')], order_by=(models.F('aaa_units')/models.F('eli_renters')).asc()),
            total=models.Window(expression=models.Count(['year']), partition_by=[models.F('year')])
        )
        
        return ranked
    
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

    objects = UrbanInstituteRentalCrisisManager()

    def aaa_units_per_100(self):
        return self.aaa_units / self.eli_renters * 100

    def noasst_units_per_100(self):
        return self.noasst_units / self.eli_renters * 100

    def hud_units_per_100(self):
        return self.hud_units / self.eli_renters * 100

    def usda_units_per_100(self):
        return self.usda_units / self.eli_renters * 100

    def no_hud_units_per_100(self):
        return self.no_hud_units / self.eli_renters * 100

    def no_usda_units_per_100(self):
        return self.no_usda_units / self.eli_renters * 100

class Policy(models.Model):
    policy_id = models.CharField(max_length=5, primary_key=True)
    policy_type = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    link1 = models.CharField(max_length=255, null=True, blank=True)
    link1_name = models.CharField(max_length=255, null=True, blank=True)
    link2 = models.CharField(max_length=255, null=True, blank=True)
    link2_name = models.CharField(max_length=255, null=True, blank=True)
    link3 = models.CharField(max_length=255, null=True, blank=True)
    link3_name = models.CharField(max_length=255, null=True, blank=True)

    # clean fields for URL filtering
    policy_type_clean = AutoSlugField(populate_from='policy_type', max_length=100)
    category_clean = AutoSlugField(populate_from='category', max_length=100)

class Program(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    government_entity = models.CharField(max_length=255)
    year_implemented = models.PositiveSmallIntegerField(null=True, blank=True)
    link1 = models.CharField(max_length=255, null=True, blank=True)
    link1_name = models.CharField(max_length=255, null=True, blank=True)
    link2 = models.CharField(max_length=255, null=True, blank=True)
    link2_name = models.CharField(max_length=255, null=True, blank=True)
    link3 = models.CharField(max_length=255, null=True, blank=True)
    link3_name = models.CharField(max_length=255, null=True, blank=True)

    # clean fields for URL filtering
    name_clean = AutoSlugField(populate_from='name', max_length=100)
    government_entity_clean = AutoSlugField(populate_from='government_entity', max_length=100)

class PermitData(models.Model):
    in_date = models.DateTimeField(null=True, blank=True)
    issue_date = models.DateTimeField()
    status = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    new_class = models.CharField(max_length=255)
    new_type = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    pdx_bnd = models.CharField(max_length=255)
    is_adu = models.CharField(max_length=5)
    rev = models.CharField(max_length=255)
    folder_number = models.CharField(max_length=20)
    property_address = models.CharField(max_length=255)
    work_description = models.TextField()
    sub = models.CharField(max_length=255)
    occ = models.CharField(max_length=255)
    new_units = models.PositiveSmallIntegerField()
    folder_des = models.CharField(max_length=255)
    valuation = models.DecimalField(max_digits=19, decimal_places=2)
    const = models.CharField(max_length=255)
    proplot = models.CharField(max_length=255)
    propgisid1 = models.CharField(max_length=255)
    property_ro = models.CharField(max_length=255)
    folder_rsn = models.IntegerField()
    x_coord = models.DecimalField(max_digits=19, decimal_places=6)
    y_coord = models.DecimalField(max_digits=19, decimal_places=6)

    point = models.PointField()

class TaxlotData(models.Model):
    year = models.PositiveSmallIntegerField()
    area = models.FloatField()
    tlid = models.CharField(max_length=16)
    rno = models.CharField(max_length=10)
    owner_address = models.CharField(max_length=35)
    owner_city = models.CharField(max_length=30)
    owner_state = models.CharField(max_length=2, null=True)
    owner_zip = models.CharField(max_length=10)
    site_str_no = models.IntegerField()
    site_address = models.CharField(max_length=35)
    site_city = models.CharField(max_length=30)
    site_zip = models.CharField(max_length=10)
    land_value = models.IntegerField()
    building_value = models.IntegerField()
    total_value = models.IntegerField()
    building_sqft = models.IntegerField()
    a_t_acres = models.FloatField()
    year_built = models.PositiveSmallIntegerField()
    prop_code = models.CharField(max_length=3)
    land_use = models.CharField(max_length=3)
    tax_code = models.CharField(max_length=7)
    sale_date = models.CharField(max_length=6)
    sale_price = models.IntegerField()
    county = models.CharField(max_length=1)
    x_coord = models.IntegerField()
    y_coord = models.IntegerField()
    or_tax_lot = models.CharField(max_length=29)
    orig_ogc_f = models.IntegerField()
    at_diff = models.IntegerField(null=True)
    area_diff = models.IntegerField(null=True)
    name = models.CharField(max_length=255)
    percent_change = models.FloatField()

    mpoly = models.MultiPolygonField()

