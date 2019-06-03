from os import listdir
import os
import random


def main():
    file_path = './ustawy/'
    changed_path = './ustawy/full_z/'
    non_changed_path = './ustawy/full_bz/'

    filename_list = listdir(changed_path)
    random.shuffle(filename_list)
    for filename in filename_list[:321]:
        os.rename(changed_path + filename, './ustawy/training/z/' + filename)
    for filename in filename_list[321:428]:
        os.rename(changed_path + filename, './ustawy/validation/z/' + filename)
    for filename in filename_list[428:]:
        os.rename(changed_path + filename, './ustawy/testing/z/' + filename)

    filename_list = listdir(non_changed_path)
    random.shuffle(filename_list)
    for filename in filename_list[:387]:
        os.rename(non_changed_path + filename, './ustawy/training/bz/' + filename)
    for filename in filename_list[387:516]:
        os.rename(non_changed_path + filename, './ustawy/validation/bz/' + filename)
    for filename in filename_list[516:]:
        os.rename(non_changed_path + filename, './ustawy/testing/bz/' + filename)


if __name__ == "__main__":
    main()
