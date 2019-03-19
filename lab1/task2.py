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
            art_list = regex.findall('art\..*', regulation)
            if len(art_list) == 0:
                art_list = regulation
            else:
                art_list = art_list[0].split(' oraz ')
            for art in art_list:
                art = regex.findall('((art\.|ust\.).*)', art)
                if len(art) > 0:
                    art = art[0][0]
                    words = art.split(' ')
                    ust_index = words.index('ust.') + 1
                    ust_list = []
                    if len(regex.findall('(, | i )', art)) > 0:
                        tmp = regex.findall('ust\..*', art)[0][0]
                        all_ust = regex.findall('[0-9]+', tmp)
                        for number in all_ust:
                            ust_list.append(number)
                    elif len(regex.findall('[0-9]+-[0-9]+', words[ust_index])) > 0:
                        start = int(regex.findall('^[0-9]+', words[ust_index])[0])
                        end = int(regex.findall('[0-9]+$', words[ust_index])[0])
                        ust_list = list(range(start, end+1))
                    else:
                        ust_list = [int(words[ust_index])]

                    if with_art:
                        art_index = words.index('art.') + 1
                        for i in ust_list:
                            self.regulations.append((filename, int(words[art_index]), i))
                    else:
                        for i in ust_list:
                            self.regulations.append((filename, 0, i))



    def find_internal_references_in_bill(self, bill, filename):
        bill = regex.sub('\n', ' ', bill)
        bill = regex.sub(' +', ' ', bill)
        bill = regex.sub('".*?"', '', bill)

        beginning = '(o któr(ym|ych|ej) mowa w|przepi(s|sy)|z zastrzeżeniem|zgodnie z|określon(e|ego)) '
        regulations = regex.findall('(' + beginning + '((art\. [0-9]+ [\p{L} ]*ust\. ([0-9]+(-[0-9]+)?( i |, )?)+)+( oraz )*))', bill)
        if len(regulations) > 0:
            regulations = [x[0] for x in regulations]
            self.parse_regulation(regulations, True, filename)
            return

        regulations = regex.findall('(' + beginning + 'ust\. ([0-9]+(-[0-9]+)?( i |, )?)+)', bill)
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

