import os
from django.contrib.gis.utils import LayerMapping
from api.models import PermitData
import boto3

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
    BUCKET_NAME = 'hacko-data-archive'
    KEY = '2018-housing-affordability/data/permits/'
    s3 = boto3.resource('s3')

    f = 'Residential_Building_Permits.geojson.json'
    file_path = '/data/permits/{}'.format(f)
    if not os.path.isfile(file_path):
        key = KEY + f
        s3.Bucket(BUCKET_NAME).download_file(key, file_path)

    PermitData.objects.all().delete()
    lm = LayerMapping(PermitData, file_path, mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=verbose)
    
