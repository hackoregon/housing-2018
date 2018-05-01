import re
import pandas as pd
#from api.models import HUDHomelessData

class DjangoImport(object):
    def __init__(self, file_loc):
        """
        Base class to import HUD Homelessness data from an Excel sheet into database via Django ORM.
        
        Parameters:
            source: name of source sheet in Excel file
            data_file: pandas ExcelFile object that contains the sheets

        """
        self.df = None
        self.file_loc = file_loc
    
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
            obj = HUDHomelessData(**body)
            yield obj

    def get_queryset(self):
        """
        Returns all objects that come from this particular import e.g. for sheet A-1 import it will return all objects with source A-1
        """
        return HUDHomelessData.objects.all()
                
    def generate_json(self):
        raise NotImplementedError("generate_json must be implemented by child class.")

    def get_base_frame(self, columns=None):
        # read sheet into dataframe
        return pd.read_excel(self.file_loc, sheet_name=self.source, header=headers[self.source], index_col=0, usecols=columns)
        
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
                qs = HUDHomelessData.objects.filter(query)
            # delete existing items in index
            qs.delete()

        # add new items
        results = HUDHomelessData.objects.bulk_create(self.generate_objects())
        return len(results)
        
    def is_valid_value(self, val):
        if pd.isnull(val) or str(val).strip() in ['', '.', 'na']:
            return False
        return True

class Pit(DjangoImport):
    def process_frame(self):
        self.df = pd.read_excel(self.file_loc, sheet_name=None)

    def generate_json(self):
        if self.file_loc.lower().endswith('by-state.xlsx'):
            geography = 'state'
        elif self.file_loc.lower().endswith('by-coc.xlsx'):
            geography = 'coc'
        else:
            raise Exception('Invalid geography')

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
                for c in df.columns[1:]:
                    datatype = re.sub(r'\,\s+' + str(year) + r'$', '', c)
                    body = {
                        'year': year,
                        'datapoint': datapoint,
                        'geography': geography,
                        'datatype': datatype,
                        'value': row[c],
                    }

                    yield body

class Hic(DjangoImport):
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

    def generate_json(self):
        if self.file_loc.lower().endswith('by-state.xlsx'):
            geography = 'state'
        elif self.file_loc.lower().endswith('by-coc.xlsx'):
            geography = 'coc'
        else:
            raise Exception('Invalid geography')

        for key, df in self.df.items():
            try:
                year = int(key)
            except ValueError:
                continue

            for datapoint, row in df.iterrows():
                for c1, c2 in df.columns[1:]:
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
                        raise Exception('No match for ' + c2 + ' in ' + c1)

                    datatype = re.sub(r'\s{2,}',' ', datatype).strip()

                    body = {
                        'year': year,
                        'datapoint': datapoint,
                        'geography': geography,
                        'datatype': datatype,
                        'shelter_status': shelter_status.replace('&', ','),
                        'value': row[(c1, c2)],
                    }
                    yield body

def load_data():
    URLS = [
        'https://www.hudexchange.info/resources/documents/2007-2017-HIC-Counts-by-CoC.XLSX',
        'https://www.hudexchange.info/resources/documents/2007-2017-HIC-Counts-by-State.xlsx',
        'https://www.hudexchange.info/resources/documents/2007-2017-PIT-Counts-by-CoC.XLSX',
        'https://www.hudexchange.info/resources/documents/2007-2017-PIT-Counts-by-State.xlsx',
    ]

    URLS = [
        '/Users/alecpeters/Downloads/2007-2017-HIC-Counts-by-CoC.XLSX',
        '/Users/alecpeters/Downloads/2007-2017-HIC-Counts-by-State.xlsx',
        '/Users/alecpeters/Downloads/2007-2017-PIT-Counts-by-CoC.XLSX',
        '/Users/alecpeters/Downloads/2007-2017-PIT-Counts-by-State.xlsx',
    ]

    imports = [
        Hic(URLS[0]),
        Hic(URLS[1]),
        Pit(URLS[2]),
        Pit(URLS[3]),
    ]

    for imp in imports:
        imp.process_frame()
        distinct = []
        for g in imp.generate_json():
            distinct.append(g['geography'])
        print(set(distinct))

load_data()
