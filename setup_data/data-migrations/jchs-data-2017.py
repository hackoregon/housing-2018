import os
import re
from datetime import datetime

import requests
import pandas as pd
import pytz
from pytz import timezone
from six.moves.urllib.request import urlopen
import elasticsearch
import elasticsearch.helpers

pacific = timezone('US/Pacific')
date_fmt = "%Y-%m-%dT%H:%M:%S.000%z"

# specify which rows in the excel sheet are the headers. 0-indexed
headers = {
    'A-1': [3,4,5],
    'A-2': [4,5],
    'W-1': [4,5],
    'W-2': [4],
    'W-3': [4],
    'W-4': [4,5],
    'W-5': [4,5],
    'W-6': [4,5],
    'W-7': [2,3,4],
    'W-8': [3,4],
    'W-9': [4],
    'W-10': [4],
    'W-11': [4],
    'W-12': [4],
    'W-13': [3,4,5],
    'W-14': [4,5,6],
    'W-15': [3,4,5],
    'W-16': [3,4],
    'W-17': [3],
    'W-18': [3],
}

# manual input of text that isn't included in the pandas-parsed table
manual_sections = {
    'W-1': 'High Poverty',
}

# Define import classes
class ElasticImport(object):
    def __init__(self, es, source, data_file):
        """
        Base class to import JCHS data from an Excel sheet into Elasticsearch.
        
        Parameters:
            es: Elasticsearch instance
            source: name of source sheet in Excel file

        """
        self.df = None
        if es is None:
            es = elasticsearch.Elasticsearch(host='localhost')
        self.es = es
        self.source = source
        self.data_file = data_file
    
    def process_frame(self):
        """
        Process the dataframe created by pandas.read_excel into the desired format for import and set to self.df
        """
        raise NotImplemented("process_frame must be implemented by child class.")
        
    def generate_doc(self):
        """
        Generator function to create actions to send to elasticsearch.helpers.bulk. Takes the json generated from 
        self.generate_json and wraps it in an elasticsearch bulk action.
        """
        for body in self.generate_json():
            action = { '_index': INDEX, '_type': 'default', '_source': body }
            yield action
                
    def generate_json(self):
        raise NotImplemented("generate_json must be implemented by child class.")

    def get_base_frame(self, columns=None):
        # read sheet into dataframe
        return pd.read_excel(self.data_file, sheet_name=self.source, header=headers[self.source], index_col=0, usecols=columns)
        
    def add_sections_to_index(self, delim=None):
        # set the proper index name and use the value pandas thought was the index name to add to the index values
        section = self.df.index.name
        if section is None and self.source in manual_sections:
            section = manual_sections[self.source]
        self.df.index.name = self.df.columns.names[-1]

        # remove rows where index is null
        self.df = self.df[self.df.index.notnull()]

        # add the multi-section labels into the index for tables that have multiple sections
        if section is not None:
            if delim is None:
                delim = ";"
            for i in range(len(self.df)):
                row = self.df.iloc[i]
                if not row.any():
                    section = row.name
                val = '{}{}{}'.format(section, delim, self.df.index[i])
                idx = self.df.index.tolist()
                idx[i] = val
                self.df.index = idx

        # drop rows where all values are empty    
        self.df = self.df.dropna(how='all')
        
    def delete_items(self, query):
        for e in elasticsearch.helpers.scan(self.es, 
                      index=INDEX,
                      doc_type='default', 
                      scroll='1m',
                      query=query,
                      _source=None):

            # There exists a parameter to avoid this del statement (`track_source`) but at my version it doesn't exists.
            del e['_score']
            e['_op_type'] = 'delete'
            yield e
            
    
    def view_data_in_elastic(self):
        result_dict = elasticsearch.helpers.scan(client=es, index=INDEX, doc_type='default', preserve_order=True, query=self.get_dataset_query(), scroll='1m')
        pandas_df = pd.DataFrame([flatten_search_results(d) for d in result_dict])
        return pandas_df
    
    def get_dataset_query(self):
        letter = self.source.split('-')[0].lower()
        num = self.source.split('-')[1]
        return {"query": {"bool": {"filter": [{ "term": { "source": letter }}, { "term": { "source": num }}]}}}
        
    def add_to_index(self, delete_existing=True, query=None, chunk_size=1000):
        """
        Adds the dataframe to the elasticsearch index using self.generate_doc to generate actions.
        
        Parameters:
            delete_existing: option to delete the existing items for this import
            query: dict-style query to know what to delete before import. Default is everything with self.source.
            chunk_size: size of batches for elasticsearch.helpers.bulk
        """
        if self.df is None:
            self.process_frame()
        if self.df is None:
            raise Exception("self.df has not been set, nothing to add to index.")
            
        if delete_existing:
            if query is None:
                query = self.get_dataset_query()
            # delete existing items in index
            elasticsearch.helpers.bulk(self.es, self.delete_items(query), chunk_size=chunk_size)

        # add new items
        result = elasticsearch.helpers.bulk(self.es, actions=self.generate_doc(), chunk_size=chunk_size)
        return result
        
    def is_valid_value(self, val):
        if pd.isnull(val) or str(val).strip() in ['', '.', 'na']:
            return False
        return True


# A-1
class ImportA1(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df = self.df.rename(columns=lambda x: re.sub('\d+$', '', x.replace('(', '').replace(')', '').strip()))
        # convert thousands
        self.df.loc[:, (slice(None), 'Thousands', slice(None))] = self.df.loc[:, (slice(None), 'Thousands', slice(None))] * 1000
        self.df.loc[:, (slice(None), 'Millions of 2016 dollars', slice(None))] = self.df.loc[:, (slice(None), 'Millions of 2016 dollars', slice(None))] * 1000000
        self.df = self.df.dropna(how='all', subset=[('Permits','Thousands','Multifamily')])
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                key = '{} {}'.format(ser_ix[2], ser_ix[0])
                value_type = ser_ix[1]
                value_type = value_type.replace('Millions of', '')
                if value_type == 'Thousands':
                    value_type = 'count'
                time = datetime(ix, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': 'United States', 'value': val, 'valuetype': value_type }
                yield body


# A-2
class ImportA2(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.add_sections_to_index()
        self.df.index = [x.split(';')[0] + ', Income ' + ' '.join(x.split(';')[1:]) for x in self.df.index]
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                val = val * 1000
                key = ix
                time = datetime(ser_ix[0], 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': ser_ix[1] + ' Households', 'datapoint': key, 'value': val, 'valuetype': 'count' }
                yield body


# W-1
class ImportW1(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.add_sections_to_index()
        self.df.index = [x.split(';')[0].split(':')[0].replace(' Neighborhoods', '') + ', ' + ' '.join(x.split(';')[1:]) + ' Neighborhoods' for x in self.df.index]
        self.df.dropna(subset=[('Number of Neighborhoods', 2015)], inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if pd.isnull(val):
                    continue
                key = ix
                time = datetime(ser_ix[1], 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': ser_ix[0], 'datapoint': key, 'value': val, 'valuetype': 'count' }
                yield body


# W-2
class ImportW2(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(subset=['Total'], inplace=True)
        self.df = self.df.loc[pd.notnull(self.df.index), :]
        self.df = self.df.loc[self.df.index.map(lambda x: 'Share of' not in x and 'Growth' not in x)]

    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                keys = ix.split(' ')
                key = keys[0]
                if key == 'Households':
                    key = 'All'
                time = datetime(int(keys[-1]), 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key + ' Households by Nativity', 'datapoint': ser_ix, 'value': val, 'valuetype': 'count' }
                yield body


# W-3
class ImportW3(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame(columns=5)
        self.df.dropna(how='all', inplace=True)
        self.df = self.df.loc[pd.notnull(self.df.index), :]
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if pd.isnull(val):
                    continue
                time = datetime(ix, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': 'Average Real Household Incomes by Income Quintile', 'datapoint': ser_ix, 'value': val, 'valuetype': '2015 Dollars' }
                yield body


# W-4
class ImportW4(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        self.df = self.df.loc[pd.notnull(self.df.index), :]
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ser_ix[1]
                if ser_ix[0] == 'All Households':
                    dp = ser_ix[0]
                time = datetime(ix, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': 'Homeownership Rates by Age, Race/Ethnicity, and Region', 'datapoint': dp, 'value': val, 'valuetype': 'Percent' }
                yield body


# W-5
class ImportW5(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.index = ['All Households' if pd.isnull(x) else x for x in self.df.index]
        self.add_sections_to_index(delim=": ")
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if pd.isnull(val):
                    continue
                val = val * 1000
                key = ser_ix[0]
                if key == 'All Households':
                    key = 'Households'
                dp = ix
                time = datetime(2015, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': ser_ix[1] + ' ' + key, 'datapoint': dp, 'value': val, 'valuetype': 'count' }
                yield body


# W-6
class ImportW6(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.add_sections_to_index(delim=": ")
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                key = ser_ix[0]
                if key == 'Non-Housing Expenditures':
                    key = ser_ix[1].replace('\n', '') + ' Expenditures'
                key = 'Monthly ' + key
                dp = ix
                dp = re.sub('\s\(.+\)', '', dp)
                dp = '{} {} {}'.format('Total Expenditures', dp, 'Share of Expenditures on Housing')
                time = datetime(2015, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': '2015 dollars' }
                yield body


# W-7
class ImportW7(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        # remove \n from columns headers
        self.df = self.df.rename(columns=lambda x: x.replace('\n', '').strip())
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if pd.isnull(val) or str(val).strip() == '':
                    continue
                time = ser_ix[2]
                key = ser_ix[0][:-1]
                if key == 'Percent Change in Home Prices':
                    key = ser_ix[1] + ' ' + key
                    key += ' from ' + time
                dp = ix.replace('Metro Area', '').strip()
                time = datetime(2016, 12, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': '2016 dollars' }
                yield body


# W-8
class ImportW8(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame(columns=[1,2,3,4,5,6,7,8,9])
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                key = ser_ix[0]
                value_type = 'percent'
                if key == 'Median Rent (Dollars)':
                    key = 'Median Rent'
                    value_type = '2015 dollars'
                dp = ix.strip()
                time = datetime(2015, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body


# W-9
class ImportW9(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                key = 'Monthly Mortgage Payment on Median Priced Home'
                dp = ix.strip()
                time = datetime(ser_ix, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': '2016 dollars' }
                yield body


# W-10
class ImportW10(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                txt = ' Able to Afford Monthly Payments on Median Priced Homes in Their Metro Area'
                value_type = '2015 dollars'
                key = ser_ix
                key = re.sub('\s\(.+\)', '', key).strip()
                if key in ['Share of All Households','Share of Renters']:
                    key += txt
                    value_type = 'percent'
                dp = ix.strip()
                time = datetime(2015, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body


# W-11
class ImportW11(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                key = 'Median Payment-to-Income Ratio'
                dp = ix.strip()
                time = datetime(ser_ix, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': 'ratio' }
                yield body


# W-12
class ImportW12(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                key = 'Median Home Price-to-Median Income Ratio'
                dp = ix.strip()
                time = datetime(ser_ix, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': 'ratio' }
                yield body


# W-13
class ImportW13(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ix.strip()
                value_type = ser_ix[0]
                key = '{} {}'.format(ser_ix[2], ser_ix[1])
                if value_type == 'Number of Households (Thousands)':
                    value_type = 'count'
                else:
                    value_type = 'percent'
                    key += ', Share of All Households'
                time = datetime(2015, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body


# W-14
class ImportW14(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ix.strip()
                value_type = 'percent'
                key = '{}, {} Households, Income {}'.format(re.sub('\s\(.+\)', '', ser_ix[0]), ser_ix[2], ser_ix[1])
                if ser_ix[0] == 'Median for All Income Groups':
                    key = ser_ix[2] + ', ' + ser_ix[0]
                    value_type = ser_ix[1].lower()
                time = datetime(2015, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body


# W-15
class ImportW15(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ix.strip()
                value_type = 'count'
                key = '{} {}'.format(ser_ix[2], ser_ix[0].replace('Number of ', '').replace('Total Population in ', ''))
                if 'Total Population' in ser_ix[0]:
                    key = 'Total Population in ' + key
                time = datetime(ser_ix[1], 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body


# W-16
class ImportW16(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame()
        self.df.dropna(how='all', inplace=True)
        # remove \n from columns headers
        self.df = self.df.rename(columns=lambda x: x.replace('\n', ' ').strip())
        self.df.set_index([('Metropolitan Area Name', 'Unnamed: 1_level_1')], append=True, inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ix[1].strip()
                key = re.sub('\s\(.+\)', '', ser_ix[0])
                if key == 'Population Rank in 2015':
                    value_type = 'rank'
                elif key == 'Share of Units by Real Rent Level':
                    value_type = 'percent'
                elif key.startswith('Change in Share'):
                    value_type = 'percentage points'
                elif key in ['Estimated Number of Renter Households by Rent Level', 'Sample Size']:
                    value_type = 'count'
                else:
                    raise Exception("No value_type found.")
                if key != 'Sample Size':
                    key = '{}, Real Gross Rents {}'.format(key, ser_ix[1])                
                    
                time = datetime(ix[0], 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': key, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body


# W-17
class ImportW17(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame(columns=[1,3,4,5])
        self.df.dropna(how='all', inplace=True)
        # remove \n from columns headers
        self.df = self.df.rename(columns=lambda x: x.replace('\n', ' ').strip())
        self.df.set_index(['Continuum of Care'], append=True, inplace=True)
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ix[0].strip()
                time = datetime(int(ser_ix.split(', ')[1]), 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': 'Continuum of Care Homelessness', 'datapoint': dp, 'value': val, 'valuetype': 'count' }
                yield body


# W-18
class ImportW18(ElasticImport):
    def process_frame(self):
        self.df = self.get_base_frame(columns=[0,1,2,5,6,8])
        self.df.dropna(how='all', inplace=True)
        # remove \n from columns headers
        self.df = self.df.rename(columns=lambda x: x.replace('\n', ' ').strip())
        
    def generate_json(self):
        for ix, row in self.df.iterrows():
            actions = []

            for ser_ix, val in row.iteritems():
                if not self.is_valid_value(val):
                    continue
                dp = ix.strip()
                key = re.sub('\s\(.+\)', '', ser_ix)
                data_type = key.split(', ')[0]
                year = int(key.split(', ')[-1])
                value_type = 'count'
                if 'Percent' in ser_ix:
                    value_type = 'percent'
                time = datetime(year, 1, 1, tzinfo=pytz.utc)
                body = { 'time': time.astimezone(pacific).strftime(date_fmt), 'source': self.source, 'datatype': data_type, 'datapoint': dp, 'value': val, 'valuetype': value_type }
                yield body

def flatten_search_results(hit):
    # from https://github.com/onesuper/pandasticsearch/blob/master/pandasticsearch/queries.py#L77
    row = {}
    for k in hit.keys():
        if k == '_source':
            row.update(hit['_source'])
        elif k.startswith('_'):
            row[k] = hit[k]
    return row

if __name__ == '__main__':
    # connect to elasticsearch and create index
    INDEX = 'jchs-data-2017'
    ES_URL = 'http://elastic:{}@elasticsearch:9200/'.format(os.environ['ELASTIC_PASSWORD'])
    es = elasticsearch.Elasticsearch([ES_URL])

    # Fetch JCHS Appendix Tables
    # If file does not already exist, go fetch it from url, otherwise load local version.
    DATA_URL_2017 = 'http://www.jchs.harvard.edu/sites/jchs.harvard.edu/files/all_son_2017_tables_current_6_12_17.xlsx'
    DATA_URL_2016 = 'http://www.jchs.harvard.edu/sites/jchs.harvard.edu/files/jchs_son2016_appendixtables_6_23_16.xlsx'
    DATA_FILE_2017 = '/usr/src/app/data-migrations/data/jchs_2017.xlsx'
    DATA_FILE_2016 = '/usr/src/app/data-migrations/data/jchs_2016.xlsx'

    if not os.path.exists(DATA_FILE_2017):
        raw = urlopen(DATA_URL_2017).read()
        with open(DATA_FILE_2017, "wb") as f:
            f.write(raw)
            print('saved excel file to ' + DATA_FILE_2017)

    # instantiate all of the import classes
    a1 = ImportA1(es=es, source='A-1', data_file=DATA_FILE_2017)
    a2 = ImportA2(es=es, source='A-2', data_file=DATA_FILE_2017)
    w1 = ImportW1(es=es, source='W-1', data_file=DATA_FILE_2017)
    w2 = ImportW2(es=es, source='W-2', data_file=DATA_FILE_2017)
    w3 = ImportW3(es=es, source='W-3', data_file=DATA_FILE_2017)
    w4 = ImportW4(es=es, source='W-4', data_file=DATA_FILE_2017)
    w5 = ImportW5(es=es, source='W-5', data_file=DATA_FILE_2017)
    w6 = ImportW6(es=es, source='W-6', data_file=DATA_FILE_2017)
    w7 = ImportW7(es=es, source='W-7', data_file=DATA_FILE_2017)
    w8 = ImportW8(es=es, source='W-8', data_file=DATA_FILE_2017)
    w9 = ImportW9(es=es, source='W-9', data_file=DATA_FILE_2017)
    w10 = ImportW10(es=es, source='W-10', data_file=DATA_FILE_2017)
    w11 = ImportW11(es=es, source='W-11', data_file=DATA_FILE_2017)
    w12 = ImportW12(es=es, source='W-12', data_file=DATA_FILE_2017)
    w13 = ImportW13(es=es, source='W-13', data_file=DATA_FILE_2017)
    w14 = ImportW14(es=es, source='W-14', data_file=DATA_FILE_2017)
    w15 = ImportW15(es=es, source='W-15', data_file=DATA_FILE_2017)
    w16 = ImportW16(es=es, source='W-16', data_file=DATA_FILE_2017)
    w17 = ImportW17(es=es, source='W-17', data_file=DATA_FILE_2017)
    w18 = ImportW18(es=es, source='W-18', data_file=DATA_FILE_2017)

    # put all the imports into a list
    imports = []
    imports.append(a1)
    imports.append(a2)
    imports.append(w1)
    imports.append(w2)
    imports.append(w3)
    imports.append(w4)
    imports.append(w5)
    imports.append(w6)
    imports.append(w7)
    imports.append(w8)
    imports.append(w9)
    imports.append(w10)
    imports.append(w11)
    imports.append(w12)
    imports.append(w13)
    imports.append(w14)
    imports.append(w15)
    imports.append(w16)
    imports.append(w17)
    imports.append(w18)

    try:
        es.indices.create(index=INDEX, ignore=400)
        # run import methods on them
        insert_ct = 0
        for i in imports:
            result = i.add_to_index()
            insert_ct += result[0]

        requests.post(ES_URL + 'datasets/default/', json={ 'ran': True, 'lastUpdate': datetime.now().strftime(date_fmt), 'title': 'jchs-data-2017', 'description': 'JCHS 2017 Appendix Tables', 'source': 'http://www.jchs.harvard.edu/sites/jchs.harvard.edu/files/all_son_2017_tables_current_6_12_17.xlsx', 'message': 'Success. {} documents added.'.format(insert_ct) })

    except BaseException as e:
        es.indices.delete(index=INDEX)
        requests.post(ES_URL + 'datasets/default/', json={ 'ran': False, 'lastUpdate': datetime.now().strftime(date_fmt), 'title': 'jchs-data-2017', 'description': 'JCHS 2017 Appendix Tables', 'source': 'http://www.jchs.harvard.edu/sites/jchs.harvard.edu/files/all_son_2017_tables_current_6_12_17.xlsx', 'message': str(e) })
