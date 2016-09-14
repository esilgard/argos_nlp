import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c
import fhcrc_clinical.SocialHistories.SystemUtilities.Globals as g
import os
import openpyxl
import collections
from os import listdir
from os.path import isfile, join
from shutil import copyfile


def populate_dir_dict():
    dev_dict = populate_split_dict(c.doc_dev_gold_dir, c.patients_dev_gold_dir)
    train_dict = populate_split_dict(c.doc_train_gold_dir, c.patients_train_gold_dir)
    test_dict = populate_split_dict(c.doc_test_gold_dir, c.patients_test_gold_dir)
    return dev_dict, train_dict, test_dict


def populate_split_dict(doc_dir, patients_dir):
    the_dict = dict()
    with open(doc_dir) as d:
        lines = d.readlines()
    for line in lines:
        id_label = line.split()
        id = id_label[0]
        label = id_label[1]
        the_dict[id] = label
    with open(patients_dir) as d:
        lines = d.readlines()
    for line in lines:
        id_label = line.split()
        id = id_label[0]
        label = id_label[1]
        the_dict[id] = label
    return the_dict


def main(dir):
    dev_dic, train_dict, test_dict = populate_dir_dict()
    onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]

    # create split dirs if they dont exist
    if not os.path.exists(c.DEV_SPLIT_DIR):
        os.makedirs(c.DEV_SPLIT_DIR)

    if not os.path.exists(c.TEST_SPLIT_DIR):
        os.makedirs(c.TEST_SPLIT_DIR)

    if not os.path.exists(c.TRAIN_SPLIT_DIR):
        os.makedirs(c.TRAIN_SPLIT_DIR)


    # make splits
    count = 0
    for file in onlyfiles:
        id = file.split("-")[0]
        id = id.split("_")[0]
        if id in dev_dic:
            copyfile(c.NOTE_OUTPUT_DIR + "\\" + file, c.DEV_SPLIT_DIR+ "\\" + file)
        elif id in train_dict:
            copyfile(c.NOTE_OUTPUT_DIR + "\\" + file, c.TRAIN_SPLIT_DIR+ "\\" + file)
        elif id in test_dict:
            copyfile(c.NOTE_OUTPUT_DIR + "\\" + file, c.TEST_SPLIT_DIR+ "\\" + file)
        else:
            if count == 0:
                copyfile(c.NOTE_OUTPUT_DIR + file, c.DEV_SPLIT_DIR+ "\\" + file)
                dev_dic[id] = c.DEV_SPLIT_DIR+ "\\" + file
            elif count == 1:
                copyfile(c.NOTE_OUTPUT_DIR + "\\" + file, c.TEST_SPLIT_DIR+ "\\" + file)
                test_dict[id] = c.TEST_SPLIT_DIR + "\\" + file
            else:
                copyfile(c.NOTE_OUTPUT_DIR + "\\" + file, c.TRAIN_SPLIT_DIR+ "\\" + file)
                train_dict[id] = c.TRAIN_SPLIT_DIR + "\\" + file
            count += 1
            count %= 5


if __name__ == '__main__':
    main(c.NOTE_OUTPUT_DIR)
