import os
import json
import elasticsearch
import elasticsearch.helpers

INDEX = os.path.splitext(os.path.basename(__file__))[0]
DATA_FILE = '/usr/src/app/data-migrations/data/cb_2016_us_cbsa_500k.json'

def delete_items():
    for e in elasticsearch.helpers.scan(es, 
                  index=INDEX,
                  doc_type='default', 
                  scroll='1m',
                  _source=None):

        # There exists a parameter to avoid this del statement (`track_source`) but at my version it doesn't exists.
        del e['_score']
        e['_op_type'] = 'delete'
        yield e

def generate_doc(features):
    for body in features:
        action = { '_index': INDEX, '_type': 'default', '_source': body }
        yield action

if __name__ == '__main__':
    es = elasticsearch.Elasticsearch(['http://elastic:{}@elasticsearch:9200/'.format(os.environ['ELASTIC_PASSWORD'])])
    es.indices.create(index=INDEX, ignore=400)

    with open(DATA_FILE) as fi:
        text = fi.read()
        data = json.loads(text)
        features = data['features']

    # delete existing items
    elasticsearch.helpers.bulk(es, delete_items())

    # add new items
    elasticsearch.helpers.bulk(es, actions=generate_doc(features))
