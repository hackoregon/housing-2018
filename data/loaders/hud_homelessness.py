import re
import os
from decimal import Decimal
import pandas as pd
from api.models import HudPitData, HudHicData
import boto3

BUCKET_NAME = 'hacko-data-archive'
KEY = '2018-housing-affordability/data/hud_homelessness/'
s3 = boto3.resource('s3')

class DjangoImport(object):
    django_model = None

    def __init__(self, file_loc, geography):
        """
        Base class to import HUD Homelessness data from an Excel sheet into database via Django ORM.

        Parameters:
            source: name of source sheet in Excel file
            file_loc: pandas ExcelFile object that contains the sheets
            geography: geography type of datapoints in this file

        """
        self.df = None
        self.file_loc = file_loc
        self.geography = geography

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
        Returns all objects that come from this particular import
        """
        return self.django_model.objects.filter(geography=self.geography)

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
            val = val.replace('%', '')
        except:
            pass
        try:
            d = Decimal(val)
            if pd.isnull(val):
                return False
            return True
        except:
            return False

class Pit(DjangoImport):
    django_model = HudPitData

    def process_frame(self):
        self.df = pd.read_excel(self.file_loc, sheet_name=None)

    def generate_json(self):
        for key, df in self.df.items():
            try:
                year = int(key)
            except ValueError:
                continue

            for ix, row in df.iterrows():
                try:
                    datapoint = row[0].strip()
                except AttributeError:
                    continue
                if ' ' in datapoint:
                    continue
                coc_name = None
                if self.geography == 'coc':
                    coc_name = row['CoC Name']

                for c in df.columns[1:]:
                    datatype = re.sub(r'\,\s+' + str(year) + r'$', '', c)
                    value = row[c]
                    if not self.is_valid_value(value):
                        continue

                    body = {
                        'year': year,
                        'datapoint': datapoint,
                        'geography': self.geography,
                        'datatype': datatype,
                        'value': value,
                    }
                    if coc_name:
                        body['datapoint'] = body['datapoint'] + ': ' + coc_name

                    yield body

class Hic(DjangoImport):
    django_model = HudHicData

    def process_frame(self):
        dic = {}

        with pd.ExcelFile(self.file_loc) as xlsx:
            for sheet in xlsx.sheet_names:
                try:
                    dic[sheet] = pd.read_excel(xlsx, header=[0,1], sheet_name=sheet)
                except ValueError as e:
                    dic[sheet] = pd.read_excel(xlsx, header=[1], sheet_name=sheet)

                    skip = []
                    use_cols = []
                    for i in range(len(dic[sheet].columns)):
                        if dic[sheet].columns[i].startswith('Unnamed:'):
                            skip.append(i)

                    for s in skip:
                        curr = -1 if len(use_cols) == 0 else use_cols[-1] + 1
                        use_cols += [i for i in range(curr + 1, s)]
                    use_cols += [i for i in range(use_cols[-1] + 2, len(dic[sheet].columns))]
                    dic[sheet] = pd.read_excel(xlsx, header=[0,1], sheet_name=sheet, usecols=use_cols)

        self.df = dic

    def generate_objects(self):
        for body in self.generate_json():
            obj = HudHicData(**body)
            yield obj

    def generate_json(self):
        for key, df in self.df.items():
            try:
                year = int(key)
            except ValueError:
                continue

            for datapoint, row in df.iterrows():
                for c1, c2 in df.columns:
                    col = c1
                    # fix for 2013 where RRH was included in total too (this isn't true for any other year)
                    if year == 2013 and c1 == 'Total Beds (ES,TH,SH)':
                        col = 'Total Beds (ES,TH,RRH,SH)'
                    match = re.search(r'\(((?:\s*(?:ES|TH|SH|RRH|OPH|PSH|DEM),?)+?)\)', col)

                    if not match:
                        if 'rapid re-housing' in c1.lower():
                            match = 'RRH'
                        if 'including demonstration programs' in c1.lower():
                            match += ' & DEM'

                    if match:
                        try:
                            group = match.groups()[0]
                        except AttributeError:
                            group = match
                        shelter_status = group.replace(' ', '')
                        datatype = c2.replace(f'({group})', '')
                        matches = group.split(',')

                        col2_match = re.search(r'\(((?:\s*(?:ES|TH|SH|RRH|OPH|PSH|DEM),?)+?)\)', datatype)
                        if col2_match:
                            shelter_status = col2_match.groups()[0]
                            datatype = datatype.replace(col2_match.group(), '')

                        edited = datatype
                        changed = False
                        for m in matches:
                            edited = re.sub(r'^\s*' + m.strip() + r'\s+', '', edited)
                            edited = re.sub(r'\s+' + m.strip() + r'\s+', ' ', edited)
                            edited = re.sub(r'\s+' + m.strip() + r'\s*$', '', edited)
                            if edited != datatype:
                                if changed:
                                    raise Exception("Cannot have two separate shelter statuses listed: " + c2)
                                shelter_status = m.strip()
                                changed = True
                        if changed:
                            #print(datatype, '---->', edited)
                            datatype = edited
                    else:
                        raise Exception('No match for ' + str(c2) + ' in ' + str(c1))

                    datatype = re.sub(r'\s{2,}',' ', datatype).strip()
                    value = row[(c1, c2)]
                    if not self.is_valid_value(value):
                        #print(f'value {value} is not valid for ({c1},{c2}), {datapoint}, {year}')
                        continue

                    body = {
                        'year': year,
                        'datapoint': datapoint,
                        'geography': self.geography,
                        'datatype': datatype,
                        'shelter_status': shelter_status.replace('&', ',').split(','),
                        'value': value,
                    }

                    yield body

def load_data():
#    URLS = [
#        'https://www.hudexchange.info/resources/documents/2007-2017-HIC-Counts-by-CoC.XLSX',
#        'https://www.hudexchange.info/resources/documents/2007-2017-HIC-Counts-by-State.xlsx',
#        'https://www.hudexchange.info/resources/documents/2007-2017-PIT-Counts-by-CoC.XLSX',
#        'https://www.hudexchange.info/resources/documents/2007-2017-PIT-Counts-by-State.xlsx',
#    ]

    files = [
        '2007-2017-HIC-Counts-by-CoC.XLSX',
        '2007-2017-HIC-Counts-by-State.xlsx',
        '2007-2017-PIT-Counts-by-CoC.XLSX',
        '2007-2017-PIT-Counts-by-State.xlsx',
    ]

    imports = [
        Hic(files[0], geography='coc'),
        Hic(files[1], geography='state'),
        Pit(files[2], geography='coc'),
        Pit(files[3], geography='state'),
    ]

    ct = 0
    for imp in imports:
        f = imp.file_loc
        file_path = '/data/hud_homelessness/{}'.format(f)
        if not os.path.isfile(file_path):
            key = KEY + f
            if not os.path.exists('/data/hud_homelessness'):
                os.mkdir('/data/hud_homelessness')
            s3.Bucket(BUCKET_NAME).download_file(key, file_path)
        imp.file_loc = file_path
        imp.process_frame()
        distinct = []
        result = imp.save()
        ct += result

    print(f'Loaded {ct} rows.')

