from os import listdir
from os.path import isfile, join
import regex


class Bills:
    def __init__(self):
        pass

    number_of_word_bill = 0


    def find_all_occur_word_bill_in_files(self, bill_files):
        for filename in bill_files:
            file = open(filename, 'r')
            bill = file.read()

            self.find_all_occur_word_bill_in_file(bill)


    def find_all_occur_word_bill_in_file(self, bill):
        bill = regex.sub('\n', ' ', bill)
        bill = regex.sub(' +', ' ', bill)

        bill_form = regex.findall(r'\bustaw(a|y|ie|om|ę|ą|ami|ach|o|)\b', bill, regex.IGNORECASE)

        self.number_of_word_bill += len(bill_form)


def main():
    bills_path = './../ustawy/'

    bill_files = [bills_path + f for f in listdir(bills_path) if isfile(join(bills_path, f))]

    bills = Bills()
    bills.find_all_occur_word_bill_in_files(bill_files)
    print(bills.number_of_word_bill)


if __name__ == "__main__":
    main()

