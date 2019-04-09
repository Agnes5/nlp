from os import listdir
import math
from genericpath import isfile
from os.path import join
from regex import regex

bigrams_for_all_files = dict()
bigrams_word1 = dict()
bigrams_word2 = dict()


# method from https://github.com/tdunning/python-llr
def denorm_entropy(counts):
    '''Computes the entropy of a list of counts scaled by the sum of the counts. If the inputs sum to one, this is just the normal definition of entropy'''
    counts = list(counts)
    total = float(sum(counts))
    # Note tricky way to avoid 0*log(0)
    return -sum([k * math.log(k/total + (k==0)) for k in counts])


# k11 – number of word A and B
# k12 – number of words B (without word A)
# k21 – number of words A (without word B)
# k22 – number of words (without word A and B)
# method from https://github.com/tdunning/python-llr
def llr_2x2(k11, k12, k21, k22):
    return 2 * (denorm_entropy([k11 + k12, k21 + k22]) +
                denorm_entropy([k11 + k21, k12 + k22]) -
                denorm_entropy([k11, k12, k21, k22]))


def llr(bigram, bigram_len):
    k11 = bigrams_for_all_files[bigram]
    k12 = 0
    k21 = 0

    for word in bigrams_word1[bigram[0]]:
        if word != bigram[1]:
            k21 += bigrams_for_all_files[(bigram[0], word)]

    for word in bigrams_word2[bigram[1]]:
        if word != bigram[0]:
            k12 += bigrams_for_all_files[(word, bigram[1])]

    k22 = bigram_len - k11 - k12 - k21
    return llr_2x2(k11, k12, k21, k22)


def pmi(bigram, bigram_len):
    count_word1 = 0
    count_word2 = 0

    for word in bigrams_word1[bigram[0]]:
        count_word1 += bigrams_for_all_files[(bigram[0], word)]

    for word in bigrams_word2[bigram[1]]:
        count_word2 += bigrams_for_all_files[(word, bigram[1])]

    return math.log2((bigrams_for_all_files[bigram] / bigram_len) /
                     (count_word1 / bigram_len * count_word2 / bigram_len))


def find_bigram(bill):
    tokens = [token for token in bill.split(' ') if token != '']

    second_tokens = tokens[1:]
    tokens = tokens[:-1]
    bigrams = [(word, word2) for word, word2 in zip(tokens, second_tokens)
               if word.isalpha() and word2.isalpha()]

    bigram_len = len(bigrams)

    for bigram in bigrams:
        if bigram in bigrams_for_all_files:
            bigrams_for_all_files[bigram] += 1
        else:
            bigrams_for_all_files[bigram] = 1
            if bigram[0] in bigrams_word1:
                bigrams_word1[bigram[0]].append(bigram[1])
            else:
                bigrams_word1[bigram[0]] = [bigram[1]]

            if bigram[1] in bigrams_word2:
                bigrams_word2[bigram[1]].append(bigram[0])
            else:
                bigrams_word2[bigram[1]] = [bigram[0]]
    return bigram_len


def parse_text(bill):
    bill = regex.sub(r'<[^>]*>', ' ', bill)
    bill = regex.sub(r'[^\p{L}0-9]', ' ', bill)
    bill = regex.sub(r' +', ' ', bill)
    bill = bill.lower()
    return bill


def main():
    bills_path = './../ustawy/'
    bigram_len = 0

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]
    for filename in bill_files:
        file = open(filename, 'r')
        bill = file.read()
        filename = regex.findall('([^./]*)(?=\.txt)', filename)[0]
        bill = parse_text(bill)
        bigram_len += find_bigram(bill)

    pmi_result = []
    llr_result = []

    for bigram in bigrams_for_all_files:
        pmi_result.append((bigram, pmi(bigram, bigram_len)))
        llr_result.append((bigram, llr(bigram, bigram_len)))

    pmi_result.sort(key=lambda x: x[1], reverse=True)
    llr_result.sort(key=lambda x: x[1], reverse=True)

    print('pmi')
    for result in pmi_result[:30]:
        print(result)

    print('llr')
    for result in llr_result[:30]:
        print(result)


if __name__ == "__main__":
    main()

