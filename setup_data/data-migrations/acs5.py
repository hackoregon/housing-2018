import os
from datetime import datetime

import pytz
from pytz import timezone
import pandas as pd
import numpy as np
import requests
from json import JSONDecodeError
import elasticsearch
import elasticsearch.helpers

def get_url(year, survey, variables, geography, location=None, is_profile=False):
    base_url = 'https://api.census.gov/data'
    # for some reason url changes in these cases
    if (survey == 'acs1' and year >= 2015) or (survey == 'acs5' and year >= 2016) or (survey == 'acs5' and is_profile and year in [2016,2015,2011]):
        survey = 'acs/' + survey
    profile = '/profile' if is_profile else ''
    url = f'{base_url}/{year}/{survey}{profile}?get={variables}&for={geography}&key={API_KEY}'
    if location is not None:
        url += f'&in={location}'
    return url

def get_results(url):
    response = requests.get(url)
    try:
        return response.json()
    except JSONDecodeError:
        return response.text

def get_variable_df(year, profile=False):
    if profile and year in [2016,2015,2011]:
        year = '{}/acs'.format(year)
    elif not profile and year >= 2016:
        year = '{}/acs'.format(year)
    variables_url = 'https://api.census.gov/data/{}/acs5{}/variables.json'.format(year, '/profile' if profile else '')
    resp = requests.get(variables_url)
    variables = resp.json()
    var_list = []
    for k, v in variables['variables'].items():
        try:
            v['id'] = k
            var_list.append(v)
        except:
            continue
    var_df = pd.DataFrame(var_list)
    #var_df.set_index('id', drop=False, inplace=True)
    return var_df

def split_filename(filename):
    parts = filename.split('_')
    return '_'.join(parts[:2]), parts[2], parts[3]
    
def get_file_definition(filename):
    data_id, state_id, year = split_filename(filename)
    row = profile_estimates.loc[data_id]
    return row

def delete_items(census_id, state_id, year):
    query = {"query": {"bool": {"filter": [{ "match": { "census_id": census_id }}, { "match": { "state_id": state_id }}, { "match": { "time": '{}-01-01'.format(year)  }}]}}}
    for e in elasticsearch.helpers.scan(es, index=INDEX, doc_type='default', scroll='1m', query=query, _source=None):
        # There exists a parameter to avoid this del statement (`track_source`) but at my version it does    n't exists.
        del e['_score']
        e['_op_type'] = 'delete'
        yield e

if __name__ == '__main__':
    API_KEY = '46828e32fefc67853bb60cd34eeb89e9db5cdcbd'
    DATA_DIR = '/usr/src/app/data-migrations'
    FILE_DIR = os.path.join(DATA_DIR, 'data/acs5')
    ES_URL = 'http://elastic:{}@elasticsearch:9200/'.format(os.environ['ELASTIC_PASSWORD'])
    INDEX = 'acs5'

    pacific = timezone('US/Pacific')
    date_fmt = "%Y-%m-%dT%H:%M:%S.000%z"
    es = elasticsearch.Elasticsearch([ES_URL])

    # downloaded from https://www.census.gov/geographies/reference-files.All.html
    geographies = pd.read_excel('https://www2.census.gov/programs-surveys/popest/geographies/2016/all-geocodes-v2016.xlsx', header=4)
    geographies.set_index(['Summary Level', 'State Code (FIPS)', 'County Code (FIPS)'], inplace=True, drop=False)
    geographies.sort_index(inplace=True)

    profile_vrs = get_variable_df(2016, profile=True)
    profile_ids = profile_vrs['id'].values
    for yr in range(2015, 2010, -1):
        df = get_variable_df(yr, profile=True)
        profile_ids = np.intersect1d(profile_ids, df['id'].values)
    profile_vrs = profile_vrs[profile_vrs['id'].isin(profile_ids)].set_index('id', drop=False).sort_index()
    profile_estimates = profile_vrs.loc[profile_vrs.index.map(lambda x: x.endswith('E'))]
    profile_estimates = profile_estimates[profile_estimates['group']!='DP02PR']

    curr_file = None
    processing_times = []
    indexing_times = []

    try:
        insert_ct = 0
        # Create index if it doesn't exist
        delete = False
        status = es.indices.create(index=INDEX, ignore=400)
        if status.get('status', 200) == 400:
            delete = True

        for file in os.listdir(FILE_DIR):
            t1 = datetime.now()
            curr_file = os.path.join(FILE_DIR, file)
            if not file.endswith('profile.csv'):
                continue
            census_id, state_id, year = split_filename(file)
            try:
                info = get_file_definition(file)
            except:
                continue
            labels = info.label.split('!!')
            data = pd.read_csv(curr_file)
            state_name = geographies.at[(40, int(state_id), 0), 'Area Name (including legal/statistical area description)'][0]
            data['county_name'] = data.apply(lambda x: geographies.at[(50, x.state, x.county), 'Area Name (including legal/statistical area description)'][0], axis=1)
            
            def get_doc():
                for row in data.iterrows():
                    d = row[1]
                    value = d[0]
                    if isinstance(value, str):
                        if value in [-999999999, -666666666, -888888888]:
                            value = ''
                        if value.endswith('+') or value.endswith('-'):
                            value = value.replace('+', '').replace('-', '')
                        try:
                            value = float(value)
                        except:
                            value = ''
                    action = { '_index': INDEX, '_type': 'default'}
                    body = {
                            'time': datetime(int(year), 1, 1, tzinfo=pytz.utc).astimezone(pacific).strftime(date_fmt),
                            'source': 'profile',
                            'census_id': census_id, 
                            'state_name': state_name,
                            'state_id': d['state'],
                            'county_name': d['county_name'],
                            'county_id': d['county'],
                            'tract_id': d['tract'],
                            'concept': info.concept,
                            'valuetype': labels[0],
                            'datatype': labels[1],
                            'group': labels[2] if len(labels) > 2 else '',
                            'value': value
                    }
                    action['_source'] = body
                    yield action

            t2 = datetime.now()        
            processing_times.append(t2 - t1)
            t1 = datetime.now()
            if delete:
                elasticsearch.helpers.bulk(es, actions=delete_items(census_id, state_id, year))
            result = elasticsearch.helpers.bulk(es, actions=get_doc())
            t2 = datetime.now()
            indexing_times.append(t2 - t1)
            insert_ct += result[0]

        requests.post(ES_URL + 'datasets/default/', json={ 'ran': True, 'lastUpdate': datetime.now().strftime(date_fmt), 'title': 'acs5', 'description': 'American Community Survey 5-Year', 'source': 'https://api.census.gov/data/2016/acs/acs5/profile/variables.html', 'message': 'Success. {} documents added.'.format(insert_ct) })

    except BaseException as e:
        # don't delete index if it fails
        #es.indices.delete(INDEX)
        msg = str(e)

        if curr_file is not None:
            msg = "Error on file " + curr_file + ": " + msg

        requests.post(ES_URL + 'datasets/default/', json={ 'ran': False, 'lastUpdate': datetime.now().strftime(date_fmt), 'title': 'acs5', 'description': 'American Community Survey 5-Year', 'source': 'https://api.census.gov/data/2016/acs/acs5/profile/variables.html', 'message': msg })

    finally:
        print(pd.Series(processing_times).describe())
        print(pd.Series(indexing_times).describe())

