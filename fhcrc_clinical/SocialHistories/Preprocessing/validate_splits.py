import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c
from os import listdir
from os.path import isfile, join


dev = [f for f in listdir(c.DEV_SPLIT_DIR) if isfile(join(c.DEV_SPLIT_DIR, f))]
test = [f for f in listdir(c.TEST_SPLIT_DIR) if isfile(join(c.TEST_SPLIT_DIR, f))]
train = [f for f in listdir(c.TRAIN_SPLIT_DIR) if isfile(join(c.TRAIN_SPLIT_DIR, f))]

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
