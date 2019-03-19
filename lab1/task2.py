import re
from itertools import groupby
from os import listdir
from os.path import isfile, join
import regex


class InternalReferences:
    def __init__(self):
        pass

    internal_references = dict()
    ex_ref = []
    regulations = []
    number = 0

    def find_internal_references_in_bills(self, bill_files):
        for filename in bill_files:
            file = open(filename, 'r')
            bill = file.read()
            filename = regex.findall('([^./]*)(?=\.txt)', filename)[0]
            self.find_internal_references_in_bill(bill, filename)


    def parse_regulation(self, regulations, with_art, filename):
        for regulation in regulations:
            words = regulation.split(' ')
            ust_index = words.index('ust.') + 1
            if with_art:
                art_index = words.index('art.') + 1
                self.regulations.append((filename, words[art_index], words[ust_index]))
            else:
                self.regulations.append((filename, '-', words[ust_index]))


    def find_internal_references_in_bill(self, bill, filename):
        bill = regex.sub('\n', ' ', bill)
        bill = regex.sub(' +', ' ', bill)
        bill = regex.sub('".*?"', '', bill)

        beginning = '(o któr(ym|ych|ej) mowa w|przepi(s|sy)|z zastrzeżeniem|zgodnie z|określon(e|ego)) '
        regulations = regex.findall('(' + beginning + 'art\. [0-9]+ [\p{L} ]*ust\. [0-9]+)(?!-| i| oraz)', bill)
        if len(regulations) > 0:
            regulations = [x[0] for x in regulations]
            self.parse_regulation(regulations, True, filename)
            return

        regulations = regex.findall('(' + beginning + 'ust\. [0-9]+)(?!-| i| oraz)', bill)
        if len(regulations) > 0:
            regulations = [x[0] for x in regulations]
            self.parse_regulation(regulations, False, filename)
            return


def main():
    bills_path = './../ustawy/'

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]

    bill_references = InternalReferences()
    bill_references.find_internal_references_in_bills(bill_files)

    bill_references.regulations.sort(reverse=True)

    result = [(key, len(list(group))) for key, group in groupby(bill_references.regulations)]

    reference_number_in_bill = dict()
    for record, number in result:
        if record[0] in reference_number_in_bill:
            reference_number_in_bill[record[0]] += number
        else:
            reference_number_in_bill[record[0]] = number
    sorted_bill = sorted(reference_number_in_bill.items(), key=lambda kv: kv[1], reverse=True)
    for key, value in sorted_bill:
        references = [(record, number) for record, number in result if record[0] == key]
        references.sort(key=lambda kv: kv[1], reverse=True)
        for reference in references:
            print(reference)


if __name__ == "__main__":
    main()

