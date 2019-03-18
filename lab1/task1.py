from os import listdir
from os.path import isfile, join
import regex


class ExternalReferences:
    def __init__(self):
        pass

    external_references = dict()
    ex_ref = []

    def find_external_references_in_bills(self, bill_files):
        for filename in bill_files:
            file = open(filename, 'r')
            bill = file.read()

            self.find_external_references_in_bill(bill)

    def parse_reference(self, reference, bill):
        reference = regex.sub('[("]Dz\.U\. ', '', reference)
        reference = regex.sub('[)"]', '', reference)
        result = []
        bills_split_by_year = reference.split('z ')
        for bills_in_year in bills_split_by_year:
            if bills_in_year == '':
                continue

            words = bills_in_year.split(' ')
            numbers_index = [index + 1 for index, x in enumerate(words) if x == 'Nr']
            poz_index = [index + 1 for index, x in enumerate(words) if x == 'poz.']

            if len(regex.findall('^[0-9][0-9][0-9][0-9]', bills_in_year)) > 0:
                year = words[0]
                for nr_i, poz_i in zip(numbers_index, poz_index):
                    number = regex.sub('[^0-9]', '', words[nr_i])
                    poz = regex.sub('[^0-9]', '', words[poz_i])
                    result.append((year, poz, number))
            else:
                reference_with_date = regex.findall('z dnia [^.]*\. [^(.]* \(Dz\.U\. ' + reference, bill)[0]
                words_in_reference_with_date = reference_with_date.split(' ')
                year = words_in_reference_with_date[words_in_reference_with_date.index('r.') - 1]
                title = regex.findall('r\. [^(]*', reference_with_date)[0]
                title = regex.sub('r. ', '', title)
                title = regex.sub(r'[^\p{L} ] ', '', title)
                title = title[:-1]
                for nr_i, poz_i in zip(numbers_index, poz_index):
                    number = regex.sub('[^0-9]', '', words[nr_i])
                    poz = regex.sub('[^0-9]', '', words[poz_i])
                    result.append((year, poz, number, title))
        return result


    def find_external_references_in_bill(self, bill):
        bill = regex.sub('\n', ' ', bill)
        bill = regex.sub(' +', ' ', bill)
        e = regex.findall('[("]Dz\.U\.[^)"]*[)"]', bill)
        result = []
        for x in e:
            result = result + self.parse_reference(x, bill)
        self.ex_ref += result


def main():
    bills_path = './../ustawy/'

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]

    bill_references = ExternalReferences()
    bill_references.find_external_references_in_bills(bill_files)

    bill_references.ex_ref.sort(reverse=True)
    for i in bill_references.ex_ref:
        print(i)


if __name__ == "__main__":
    main()

