import os
import shutil
import requests
from django.contrib.gis.utils import LayerMapping
from api.models import TaxlotData

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
    'juris_city': 'JURIS_CITY',
    'gis_acres': 'GIS_ACRES',
    'state_class': 'STATECLASS',
    'or_tax_lot': 'ORTAXLOT',
    'orig_ogc_f': 'orig_ogc_f',
    'building_value_2011': 'BVAL_2011',
    'land_value_2011': 'LVAL_2011',
    'total_value_2011': 'TVAL_2011',
    'percent_change_2011_2017': 'PCNTCHANGE',
    'mpoly': 'MULTIPOLYGON',
}

def run(verbose=True):
    try:
        TMP_LOCATION = '/tmp/taxlots_2017v2011/'
        if not os.path.isdir(TMP_LOCATION):
            os.makedirs(TMP_LOCATION)
            
        for ext in ['shp','shx']:
            file_name = 'taxlots_2017v2011.{}'.format(ext)
            file_loc = TMP_LOCATION + file_name
            if not os.path.isfile(file_loc):
                url = 'https://hackoregon-housingaffordability-2018.nyc3.digitaloceanspaces.com/taxlots/{}'.format(file_name)
                with open(file_loc, 'w') as f:
                    f.write(requests.get(url).text)

        TaxlotData.objects.all().delete()
        lm = LayerMapping(TaxlotData, TMP_LOCATION + 'taxlots_2017v2011.shp', mapping, transform=False, encoding='iso-8859-1')
        lm.save(strict=True, verbose=verbose)

    finally:
        if os.path.isdir(TMP_LOCATION): 
            shutil.rmtree(TMP_LOCATION)

