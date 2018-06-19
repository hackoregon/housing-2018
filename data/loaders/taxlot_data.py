import os
import shutil
import requests
from django.contrib.gis.utils import LayerMapping
from django.db.models.signals import pre_save
from api.models import TaxlotData
    
years = ['2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']

mapping = {
    'area': 'AREA',
    'tlid': 'TLID',
    'rno': 'RNO',
    'owner_address': 'OWNERADDR',
    'owner_city': 'OWNERCITY',
    'owner_state': 'OWNERSTATE',
    'owner_zip': 'OWNERZIP',
    'site_str_no': 'SITESTRNO',
    'site_address': 'SITEADDR',
    'site_city': 'SITECITY',
    'site_zip': 'SITEZIP',
    'land_value': 'LANDVAL',
    'building_value': 'BLDGVAL',
    'total_value': 'TOTALVAL',
    'building_sqft': 'BLDGSQFT',
    'a_t_acres': 'A_T_ACRES',
    'year_built': 'YEARBUILT',
    'prop_code': 'PROP_CODE',
    'land_use': 'LANDUSE',
    'tax_code': 'TAXCODE',
    'sale_date': 'SALEDATE',
    'sale_price': 'SALEPRICE',
    'county': 'COUNTY',
    'x_coord': 'X_COORD',
    'y_coord': 'Y_COORD',
    'orig_ogc_f': 'orig_ogc_f',
    'percent_change': 'PCNTCHANGE',
    'mpoly': 'MULTIPOLYGON',
}

def run(verbose=False):
    TaxlotData.objects.all().delete()

    for year in years:
        # Override field settings to add in year
        class YearLayerMapping(LayerMapping):
            def feature_kwargs(self, feat):
                kwargs = super().feature_kwargs(feat)
                kwargs['year'] = year
                return kwargs

        try:
            TMP_LOCATION = 'data/taxlots_{}/'.format(year)
            if not os.path.isdir(TMP_LOCATION):
                os.makedirs(TMP_LOCATION)
                
            for ext in ['shp','shx','dbf','prj','qpj']:
                file_name = 'taxlots_Portland_sfr.{}'.format(ext)
                file_loc = TMP_LOCATION + file_name
                if not os.path.isfile(file_loc):
                    url = 'https://hackoregon-housingaffordability-2018.nyc3.digitaloceanspaces.com/taxlots/{}'.format(file_name)
                    print("Downloading " + url)
                    with open(file_loc, 'w') as f:
                        f.write(requests.get(url).text)
            print("Finished downloading all files.")
            print(os.listdir(TMP_LOCATION))

            m = mapping.copy()
            if year in ['2005','2006']:
                m.pop('owner_state')
                m.pop('site_zip')

            lm = YearLayerMapping(TaxlotData, TMP_LOCATION + 'taxlots_Portland_sfr.shp', m, transform=False, encoding='iso-8859-1')
            lm.save(strict=True, verbose=verbose)

        finally:
            print("Not deleting taxlots files.")
            #if os.path.isdir(TMP_LOCATION): 
                #shutil.rmtree(TMP_LOCATION)

