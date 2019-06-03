from os import listdir
from os.path import isfile
import os
import regex

import re


def main():
    text = 'o zmianie ustawy'
    file_path = './ustawy/bez_zmiany/'
    changed_path = './ustawy/o_zmianie/'
    non_changed_path = './ustawy/bez_zmiany/'

    for filename in listdir(file_path):
        if isfile(file_path + filename):
            print(filename)
            f = open(file_path + filename, 'r')
            text = f.readlines()
            text = re.sub('\n', ' ', text)
            text = re.sub('  +', ' ', text)
            print(text)
            found = regex.findall('[Uu][Ss][Tt][Aa][Ww][Aa] +z +dnia +[0-9]+ +\p{L}+ +[0-9]{4} +r\. +o zmianie ustawy.* Art. 1.', text)
            if found:
                os.rename(file_path + filename, changed_path + filename)
            else:
                os.rename(file_path + filename, non_changed_path + filename)

            text = re.sub('(?<=USTAWA)(.*)(?=Art\. 1\.)', ' ', text)
            text = regex.sub('(.*)(?=Art\. 1\.)', ' ', text)
            is_write = False
            f = open('./ustawy/full_bz/' + filename, 'w')

            for line in text:
                if is_write:
                    f.write(line)
                elif regex.findall('Art\. 1\.', line):
                    is_write = True


if __name__ == "__main__":
    main()