import pandas as pd
import os
from api.models import UrbanInstituteRentalCrisisData
import boto3

BUCKET_NAME = 'hacko-cdn'
KEY = '2018-housing-affordability/data/urbaninstitute/'
s3 = boto3.resource('s3')

class DjangoImport(object):
    django_model = None

    def __init__(self, file_loc):
        """
        Base class to import HUD Homelessness data from an Excel sheet into database via Django ORM.
        
        Parameters:
            source: name of source sheet in Excel file
            file_loc: pandas ExcelFile object that contains the sheets
        """
        self.df = None
        self.file_loc = file_loc
        if file_loc.endswith('_2000.csv'):
            year = 2000
        elif file_loc.endswith('_2010-14.csv'):
            year = 2014
        elif file_loc.endswith('_2005-09.csv'):
            year = 2009
        else:
            raise Exception('No valid year found in file name ' + file_loc)

        self.year = year
    
    def process_frame(self):
        """
        Process the dataframe created by pandas.read_excel into the desired format for import and set to self.df
        """
        raise NotImplementedError("process_frame must be implemented by child class.")
        
    def generate_objects(self):
        """
        Generator function to create Django objects to save to the database. Takes the json generated from 
        self.generate_json and creates objects out of it.
        """
        for body in self.generate_json():
            obj = self.django_model(**body)
            yield obj

    def get_queryset(self):
        """
        Returns all objects that come from this particular import e.g. for sheet A-1 import it will return all objects with source A-1
        """
        return self.django_model.objects.filter(year=self.year)
                
    def generate_json(self):
        raise NotImplementedError("generate_json must be implemented by child class.")

    def save(self, delete_existing=True, query=None):
        """
        Adds the dataframe to the database via the Django ORM using self.generate_objects to generate Django objects.
        
        Parameters:
            delete_existing: option to delete the existing items for this import
            query: Django Q object filter of JCHSData objects to know what to delete before import. Default is everything with self.source.
        """
        if self.df is None:
            self.process_frame()
        if self.df is None:
            raise Exception("self.df has not been set, nothing to add to database.")
            
        if delete_existing:
            if query is None:
                qs = self.get_queryset()
            else:
                qs = django_model.objects.filter(query)
            # delete existing items in index
            qs.delete()

        results = self.django_model.objects.bulk_create(self.generate_objects(), batch_size=10000)
        return len(results)
        
    def is_valid_value(self, val):
        try:
            d = Decimal(val)
            if pd.isnull(val):
                return False
            return True
        except:
            return False

class UrbanInstituteImport(DjangoImport):
    django_model = UrbanInstituteRentalCrisisData

    def process_frame(self):
        df = pd.read_csv(self.file_loc, encoding='iso-8859-1')
        df.columns = [c.lower() for c in df.columns]
        self.df = df

    def generate_json(self):
        for ix, row in self.df.iterrows():
            state_flag = row['state_flag'] != 0
            eli_limit = row['l30_4']
            if pd.isnull(eli_limit):
                continue
            eli_renters = row['st_total' if state_flag else 'total']
            aaa_units = row['st_units' if state_flag else 'units']
            noasst_units = row['st_unitsnoasst' if state_flag else 'unitsnoasst']
            hud_units = row['st_hud' if state_flag else 'hud']
            usda_units = row['st_usda' if state_flag else 'usda']
            no_hud_units = row['st_units_no_hud' if state_flag else 'units_no_hud']
            no_usda_units = row['st_units_no_usda' if state_flag else 'units_no_usda']
            county_name = row['countyname']
            if not county_name.lower().endswith('county'):
                county_name = county_name + ' County'
                
            body = {
                'year': self.year,
                'eli_limit': eli_limit if pd.notnull(eli_limit) else None,
                'county_fips': row['county'],
                'county_name': county_name,
                'state_name': row['state_name'], 
                'is_state_data': state_flag,
                'eli_renters': eli_renters if pd.notnull(eli_renters) else None, 
                'aaa_units': aaa_units if pd.notnull(aaa_units) else None,
                'noasst_units': noasst_units if pd.notnull(noasst_units) else None, 
                'hud_units': hud_units if pd.notnull(hud_units) else None,
                'usda_units': usda_units if pd.notnull(usda_units) else None,
                'no_hud_units': no_hud_units if pd.notnull(no_hud_units) else None,
                'no_usda_units': no_usda_units if pd.notnull(no_usda_units) else None,
            }

            yield body

def load_data():
    files = [
        'HAI_map_2000.csv',
        'HAI_map_2005-09.csv',
        'HAI_map_2010-14.csv',
    ]

    for f in files:
        key = KEY + f
        file_path = '/data/urbaninstitute/{}'.format(f)
        if not os.path.isfile(file_path):
            s3.Bucket(BUCKET_NAME).download_file(key, file_path)
        i = UrbanInstituteImport(file_loc=file_path)
        i.save()

