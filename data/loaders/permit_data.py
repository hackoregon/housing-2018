from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos.libgeos import load_geos
from api.models import PermitData

file_location = 'https://hackoregon-housingaffordability-2018.nyc3.digitaloceanspaces.com/Residential_Building_Permits.geojson.json'

mapping = {
    'in_date': 'INDATE',
    'issue_date': 'ISSUEDATE',
    'status': 'STATUS',
    'year': 'YEAR_',
    'new_class': 'NEWCLASS',
    'new_type': 'NEWTYPE',
    'neighborhood': 'NBRHOOD',
    'pdx_bnd': 'PDXBND',
    'is_adu': 'IS_ADU',
    'rev': 'REV',
    'folder_number': 'FOLDERNUMB',
    'property_address': 'PROP_ADDRE',
    'work_description': 'WORKDESC',
    'sub': 'SUB',
    'occ': 'OCC',
    'new_units': 'NEW_UNITS',
    'folder_des': 'FOLDER_DES',
    'valuation': 'VALUATION',
    'const': 'CONST',
    'proplot': 'PROPLOT',
    'propgisid1': 'PROPGISID1',
    'property_ro': 'PROPERTYRO',
    'folder_rsn': 'FOLDERRSN',
    'x_coord': 'X_COORD',
    'y_coord': 'Y_COORD',
    'point': 'POINT',
}

def run(verbose=True):
    PermitData.objects.all().delete()
    # for some reason lm.save will not work in Docker in DigitalOcean unless we run load_geos first.
    load_geos()
    lm = LayerMapping(PermitData, file_location, mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=verbose)
    
