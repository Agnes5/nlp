from os import listdir
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np


category = dict() # category - number of occuring
entities = dict() # word - (category, number of occuring)

def main():
    result_file_path = './wyniki/'

    for filename in listdir(result_file_path):
        root = ET.parse(result_file_path + filename).getroot()
        prev = ''
        for tok in root.findall('chunk/sentence/tok'):
            is_ann = 0
            for ann in tok.findall('ann'):
                if int(ann.text) > 0:
                    is_ann = 1

                    ann = ann.get('chan')
                    orth = tok.findall('orth')[0].text
                    lex = tok.findall('lex/base')[0].text

                    if prev != '' and ann == prev[1]:
                        prev = (prev[0] + ' ' + orth, ann)
                    elif prev == '':
                        prev = (orth, ann)

            if is_ann == 0 and prev != '':
                if prev[1] in category:
                    category[prev[1]] += 1
                else:
                    category[prev[1]] = 1
                if prev in entities:
                    entities[prev] += 1
                else:
                    entities[prev] = 1
                prev = ''

    # hist 1
    sorted_category = sorted(category.items(), key=lambda kv: kv[1], reverse=True)
    x = list(map(list, zip(*sorted_category)))
    categories_name = x[0]
    categories_value = x[1]

    indices = np.arange(len(category))
    plt.barh(indices, categories_value)
    plt.yticks(indices, categories_name)
    plt.tight_layout()
    plt.show()

    # hist 2
    general_category = dict()

    for name, number in zip(categories_name, categories_value):
        parts = name.split('_')
        general_name = parts[0] + '_' + parts[1]
        if general_name in general_category:
            general_category[general_name] += number
        else:
            general_category[general_name] = number

    sorted_category = sorted(general_category.items(), key=lambda kv: kv[1], reverse=True)
    x = list(map(list, zip(*sorted_category)))
    general_category_name = x[0]
    number_of_general_category_name = x[1]

    indices = np.arange(len(general_category_name))
    plt.barh(indices, number_of_general_category_name)
    plt.yticks(indices, general_category_name)
    plt.tight_layout()
    plt.show()

    sorted_entities = sorted(entities.items(), key=lambda kv: kv[1], reverse=True)
    for entity in sorted_entities[:50]:
        print('{}\t\t{}\t\t{}'.format(entity[0][0], entity[0][1], entity[1]))

    for category_name in general_category_name:
        i = 0
        print(category_name)
        for entity in sorted_entities:
            if i == 10:
                break
            if category_name in entity[0][1]:
                print(str(entity[0][0]) + '\t' + str(entity[1]))
                i += 1



if __name__ == "__main__":
    main()

