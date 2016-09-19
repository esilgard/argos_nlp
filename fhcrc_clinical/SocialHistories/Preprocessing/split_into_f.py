import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c
import fhcrc_clinical.SocialHistories.SystemUtilities.Globals as g
import os
import openpyxl
import collections
from os import listdir
from os.path import isfile, join
from shutil import copyfile


def populate_dir_dict():
    gold_annotation_dir = os.path.join(c.DATA_DIR, "resources", "Florian_Data", "Florian", "smoking_status",
                                       "SmokingStatusAnnotator", "resources", "gold")
    doc_dev_gold_dir = gold_annotation_dir + "documents_dev.gold"
    doc_test_gold_dir = gold_annotation_dir + "documents_testing.gold"
    doc_train_gold_dir = gold_annotation_dir + "documents_training.gold"
    patients_dev_gold_dir = gold_annotation_dir + "patients_dev.gold"
    patients_test_gold_dir = gold_annotation_dir + "patients_testing.gold"
    patients_train_gold_dir = gold_annotation_dir + "patients_training.gold"

    dev_dict = populate_split_dict(doc_dev_gold_dir, patients_dev_gold_dir)
    train_dict = populate_split_dict(doc_train_gold_dir, patients_train_gold_dir)
    test_dict = populate_split_dict(doc_test_gold_dir, patients_test_gold_dir)
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
    NOTE_OUTPUT_DIR = os.path.join(c.DATA_DIR, "output")
    TRAIN_SPLIT_DIR = os.path.join(c.DATA_DIR, "notes_training", "")
    DEV_SPLIT_DIR = os.path.join(c.DATA_DIR, "notes_dev", "")
    TEST_SPLIT_DIR = os.path.join(c.DATA_DIR, "notes_testing", "")


    dev_dic, train_dict, test_dict = populate_dir_dict()
    onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]

    # create split dirs if they dont exist
    if not os.path.exists(DEV_SPLIT_DIR):
        os.makedirs(DEV_SPLIT_DIR)

    if not os.path.exists(TEST_SPLIT_DIR):
        os.makedirs(TEST_SPLIT_DIR)

    if not os.path.exists(TRAIN_SPLIT_DIR):
        os.makedirs(TRAIN_SPLIT_DIR)


    # make splits
    count = 0
    for file in onlyfiles:
        id = file.split("-")[0]
        id = id.split("_")[0]
        if id in dev_dic:
            copyfile(NOTE_OUTPUT_DIR + "\\" + file, DEV_SPLIT_DIR+ "\\" + file)
        elif id in train_dict:
            copyfile(NOTE_OUTPUT_DIR + "\\" + file, TRAIN_SPLIT_DIR+ "\\" + file)
        elif id in test_dict:
            copyfile(NOTE_OUTPUT_DIR + "\\" + file, TEST_SPLIT_DIR+ "\\" + file)
        else:
            if count == 0:
                copyfile(NOTE_OUTPUT_DIR + file, DEV_SPLIT_DIR+ "\\" + file)
                dev_dic[id] = DEV_SPLIT_DIR+ "\\" + file
            elif count == 1:
                copyfile(NOTE_OUTPUT_DIR + "\\" + file, TEST_SPLIT_DIR+ "\\" + file)
                test_dict[id] = TEST_SPLIT_DIR + "\\" + file
            else:
                copyfile(NOTE_OUTPUT_DIR + "\\" + file, TRAIN_SPLIT_DIR+ "\\" + file)
                train_dict[id] = TRAIN_SPLIT_DIR + "\\" + file
            count += 1
            count %= 5


if __name__ == '__main__':
    main(os.path.join(c.DATA_DIR, "output"))
