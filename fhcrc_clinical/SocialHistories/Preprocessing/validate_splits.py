import os

import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c
from os import listdir
from os.path import isfile, join

NOTE_OUTPUT_DIR = os.path.join(c.DATA_DIR, "output")
TRAIN_SPLIT_DIR = os.path.join(c.DATA_DIR, "notes_training", "")
DEV_SPLIT_DIR = os.path.join(c.DATA_DIR, "notes_dev", "")
TEST_SPLIT_DIR = os.path.join(c.DATA_DIR, "notes_testing", "")

dev = [f for f in listdir(DEV_SPLIT_DIR) if isfile(join(DEV_SPLIT_DIR, f))]
test = [f for f in listdir(TEST_SPLIT_DIR) if isfile(join(TEST_SPLIT_DIR, f))]
train = [f for f in listdir(TRAIN_SPLIT_DIR) if isfile(join(TRAIN_SPLIT_DIR, f))]

for file in dev:
    for f2 in test:
        if file == f2:
            print "ERROR: \n"
            print "\t" + f2 + " in TEST == " + file + " in DEV"

for file in dev:
    for f2 in train:
        if file == f2:
            print "ERROR: \n"
            print "\t" + f2 + " in TRAIN == " + file + " in DEV"

for file in train:
    for f2 in test:
        if file == f2:
            print "ERROR: \n"
            print "\t" + f2 + " in TEST == " + file + " in TRAIN"
