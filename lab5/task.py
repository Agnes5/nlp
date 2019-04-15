from collections import defaultdict
from os import listdir

import math
import requests
from genericpath import isfile

from os.path import join
import regex
import pickle
from tqdm import tqdm





def read_response(response):
    words = regex.findall(r'(?<=\n\t)([^\t]*)', response)
    tags = regex.findall(r'(?<=[^\n]\t)([^:\t\n]*)(?=[:\t])', response)
    return list(zip(words, tags))

def compute_llr():
    bigrams = dict()
    count_all_bigrams = 0
    first_words = defaultdict(list)
    second_words = defaultdict(list)
    with open('./bigrams', 'rb') as bigrams_file:
        bigrams = pickle.load(bigrams_file)

    for word1, tag1, word2, tag2 in bigrams.keys():
        count_all_bigrams += bigrams[(word1, tag1, word2, tag2)]
        first_words[(word1, tag1)].append((word2, tag2))
        second_words[(word2, tag2)].append((word1, tag1))

    # method from https://github.com/tdunning/python-llr
    def denorm_entropy(counts):
        '''Computes the entropy of a list of counts scaled by the sum of the counts. If the inputs sum to one, this is just the normal definition of entropy'''
        counts = list(counts)
        total = float(sum(counts))
        # Note tricky way to avoid 0*log(0)
        return -sum([k * math.log(k / total + (k == 0)) for k in counts])

    # k11 – number of word A and B
    # k12 – number of words B (without word A)
    # k21 – number of words A (without word B)
    # k22 – number of words (without word A and B)
    # method from https://github.com/tdunning/python-llr
    def llr_2x2(k11, k12, k21, k22):
        return 2 * (denorm_entropy([k11 + k12, k21 + k22]) +
                    denorm_entropy([k11 + k21, k12 + k22]) -
                    denorm_entropy([k11, k12, k21, k22]))

    def llr():
        k11 = bigrams[bigram]
        k12 = 0
        k21 = 0

        for word, tag in first_words[(word1, tag1)]:
            if word != word2 or tag != tag2:
                k21 += bigrams[(word1, tag1, word, tag)]

        for word, tag in second_words[(word2, tag2)]:
            if word != word1 or tag != tag1:
                k12 += bigrams[(word, tag, word2, tag2)]

        k22 = count_all_bigrams - k11 - k12 - k21
        return llr_2x2(k11, k12, k21, k22)



    result = dict()
    for word1, tag1, word2, tag2 in tqdm(bigrams.keys()):
        bigram = (word1, tag1, word2, tag2)
        result[bigram] = llr()

    print('compute llr')

    with open('./llr', 'wb') as bigrams_file:
        pickle.dump(result, bigrams_file)

    sorted_result = sorted(result.items(), key=lambda kv: kv[1], reverse=True)
    i = 0
    for bigram, value in sorted_result:
        if bigram[1] == 'subst' and (bigram[3] == 'subst' or bigram[3] == 'adj'):
            print(bigram, value)
            i += 1
        if i == 50:
            break


def main():
    bills_path = './../ustawy/'
    bigrams_with_tags = dict()

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]
    for filename in tqdm(bill_files):
        file = open(filename, 'r')
        bill = file.read()
        r = requests.post('http://localhost:9200', data=bill.encode('utf-8'))
        response = r.text
        words_with_tag = read_response(response)
        first_words = words_with_tag[:-1]
        second_words = words_with_tag[1:]
        bigrams_list = [(word, word2) for word, word2 in zip(first_words, second_words)
                   if word[1] != 'interp' and word[1] != 'num'
                   and word2[1] != 'interp' and word2[1] != 'num'
                   and word[0].isalpha() and word2[0].isalpha()]
        for word1, word2 in bigrams_list:
            if (word1[0], word1[1], word2[0], word2[1]) in bigrams_with_tags:
                bigrams_with_tags[(word1[0], word1[1], word2[0], word2[1])] += 1
            else:
                bigrams_with_tags[(word1[0], word1[1], word2[0], word2[1])] = 1

    with open('./bigrams', 'wb') as bigrams_file:
        pickle.dump(bigrams_with_tags, bigrams_file)

    compute_llr()


if __name__ == "__main__":
    main()

