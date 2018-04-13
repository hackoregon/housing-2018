import pandas as pd
import requests
import elasticsearch
import elasticsearch.helpers

if __name__ == '__main__':
    API_KEY = '46828e32fefc67853bb60cd34eeb89e9db5cdcbd'
    DATA_URL = 'https://hackoregon-housingaffordability-2018.nyc3.digitaloceanspaces.com/ipums_data/usa_00003.csv'
    ES_URL = 'http://elastic:{}@elasticsearch:9200/'.format(os.environ['ELASTIC_PASSWORD'])
    INDEX = 'ipums_hhincome'

    incomes = pd.read_csv(DATA_URL)
    print('Loaded dataframe.')

    es = elasticsearch.Elasticsearch([ES_URL])
    indexing_times = []

    result_json = { 
        'lastUpdate': datetime.now().strftime(date_fmt), 
        'title': INDEX, 
        'description': 'IPUMS ACS 5-Year Household Income Data', 
        'source': 'https://usa.ipums.org/usa/' 
    }

    try:
        es.indices.create(index=INDEX, ignore=400)

        def get_doc():
            for row in incomes.iterrows():
                d = row[1]
                action = { '_index': INDEX, '_type': 'default'}
                body = {
                    'year': d.YEAR,
                    'serial': d.SERIAL,
                    'hhwt': d.HHWT,
                    'statefip': d.STATEFIP,
                    'countyfips': d.COUNTYFIPS,
                    'metaread': d.METAREAD,
                    'hhincome': d.HHINCOME,
                    'pernum': d.PERNUM,
                    'perwt': d.PERWT,
                }
                action['_source'] = body
                yield action

        t1 = datetime.now()
        result = elasticsearch.helpers.bulk(es, actions=get_doc())
        t2 = datetime.now()
        indexing_times.append(t2 - t1)
        result_json['ran'] = True
        result_json['message'] = 'Success. {} documents added.'.format(result[0])
        requests.post(ES_URL + 'datasets/default/', json=result_json)

    except BaseException as e:
        es.indices.delete(index=INDEX)
        result_json['ran'] = False
        result_json['message'] = str(e)
        requests.post(ES_URL + 'datasets/default/', json=result_json)

    finally:
        print(pd.Series(indexing_times).describe())
