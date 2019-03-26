from os import listdir

import json
from elasticsearch import Elasticsearch, TransportError
from genericpath import isfile

from os.path import join

from regex import regex


def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}], timeout=60)
    print(es)
    index_name = 'bill-index'

    an = {
        "settings": {
            "index" : {
                "analysis" : {
                    "filter" : {
                        "synonym_filter" : {
                            "type" : "synonym",
                            "synonyms" : [
                                "kpk, kodeks postępowania karnego",
                                "kpc, kodeks postępowania cywilnego",
                                "kpk, kodeks karny",
                                "kpk, kodeks cywilny"
                            ]
                        }
                    },
                    "analyzer" : {
                        "synonym_analyzer" : {
                            "tokenizer" : "standard",
                            "filter" : ["synonym_filter", "morfologik_stem", "lowercase"]
                        }
                    }
                }
            }

        },
        "mappings": {
            "doc": {
                "properties": {
                  "title": {
                    "type": "text",
                    "analyzer": "synonym_analyzer"
                  }
                }
            }
        }
    }

    res = es.indices.create(index=index_name, body=an)

    bills_path = './../ustawy/'

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]
    for filename in bill_files:
        file = open(filename, 'r')
        bill = file.read()
        filename = regex.findall('([^./]*)(?=\.txt)', filename)[0]
        data = {'title': bill}
        json_data = json.dumps(data)

        res = es.index(index=index_name, doc_type='doc', id=filename, body=json_data)

    res = es.search(index=index_name, body={"query": {"match": {'title': 'ustawa'}}})
    res = es.search(index=index_name, body={"query": {"match_phrase": {'title': 'kodeks postępowania cywilnego'}}})
    res = es.search(index=index_name, body={"query": {"match_phrase": {'title': {'query': 'wchodzi w życie', 'slop': 2}}}})
    res = es.search(index=index_name, body={'size': 10, "query": {"match": {'title': 'konstytucja'}}})

    res = es.search(index=index_name, body={'size': 10,

                                            "query": {"match": {'title': 'konstytucja'}},
                                            "highlight": {
                                                "number_of_fragments": 3,
                                                "fields": {
                                                    "title": {}
                                                }
                                            },
                                            })


if __name__ == "__main__":
    main()