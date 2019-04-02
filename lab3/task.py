from os import listdir
import json
import operator
import numpy as np
import pylab
import requests
from elasticsearch import Elasticsearch, TransportError
from genericpath import isfile
from os.path import join
from regex import regex
import matplotlib.pyplot as plt

an = {
    "settings": {
        "index": {
            "analysis": {
                "filter": {
                    "synonym_filter": {
                        "type": "synonym",
                        "synonyms": [
                            "kpk, kodeks postępowania karnego",
                            "kpc, kodeks postępowania cywilnego",
                            "kpk, kodeks karny",
                            "kpk, kodeks cywilny"
                        ]
                    }
                },
                "analyzer": {
                    "synonym_analyzer": {
                        "tokenizer": "standard",
                        "filter": ["synonym_filter", "morfologik_stem", "lowercase"]
                    }
                }
            }
        }

    },
    "mappings": {
        "doc": {
            "properties": {
                "text": {
                    "type": "text",
                    "term_vector": "with_positions_offsets_payloads",
                    "store": True,
                    "analyzer": "synonym_analyzer"
                }
            }
        }
    }
}


def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}], timeout=60)
    index_name = 'test-index6'
    filename_list = []

    res = es.indices.create(index=index_name, body=an)

    bills_path = './../ustawy/'

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]
    for filename in bill_files:
        file = open(filename, 'r')
        bill = file.read()
        filename = regex.findall('([^./]*)(?=\.txt)', filename)[0]
        filename_list.append(filename)
        data = {'text': bill}
        json_data = json.dumps(data)

        res = es.index(index=index_name, doc_type='doc', id=filename, body=json_data)

    res = es.mtermvectors(index=index_name, doc_type='doc', body={'ids': filename_list}, field_statistics=False, payloads=False, offsets=False, term_statistics=False, positions=False)

    frequency_list = dict()
    for docs in res['docs']:
        words = docs['term_vectors']['text']['terms']
        for word in words:
            if word.isalpha() and len(word) >= 2:
                if word in frequency_list:
                    frequency_list[word] += int(words[word]['term_freq'])
                else:
                    frequency_list[word] = int(words[word]['term_freq'])

    sorted_list = sorted(frequency_list.items(), key=operator.itemgetter(1), reverse=True)

    values = [value for key, value in sorted_list]
    keys = [key for key, value in sorted_list]

    draw_graph(values)

    words = []

    file = open('./../polimorfologik-2.1 (1)/polimorfologik-2.1.txt', 'r')
    for line in file.readlines():
        word = line.split(';')[0]
        words.append(word.lower())

    words_not_in_dict = []
    words_in_dict = []

    for word in keys:
        if word not in words:
            words_not_in_dict.append((word, frequency_list[word]))
        else:
            words_in_dict.append((word, frequency_list[word]))


    words_not_in_dict.sort(key=lambda tup: tup[1], reverse=True)

    first_30 = words_not_in_dict[:30]

    words_not_in_dict.sort(key=lambda tup: tup[1], reverse=False)

    word_with_3_occurance = [word for word, value in words_not_in_dict if value == 3]

    word_with_3_occurance = word_with_3_occurance[:30]

    correct = []
    for word in word_with_3_occurance:
        ration = 100
        most_correct_word = ''
        for correct_word, tmp in words_in_dict:
            levenshtein_ratio = levenshtein(word, correct_word)
            if levenshtein_ratio < ration and levenshtein_ratio != 0:
                ration = levenshtein_ratio
                most_correct_word = correct_word
            if ration == 1:
                correct.append(correct_word)
                break
        if ration != 1:
            correct.append(most_correct_word)


def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return matrix[size_x - 1, size_y - 1]


def draw_graph(values):
    plt.plot(values)

    plt.yscale('log')
    plt.xscale('log')

    plt.show()


if __name__ == "__main__":
    main()