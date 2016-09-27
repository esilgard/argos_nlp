import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c
import fhcrc_clinical.SocialHistories.SystemUtilities.Globals as g
import os
import openpyxl
import collections
from os import listdir
from os.path import isfile, join
from shutil import copyfile

def main(dirs):
    dev = [f for f in listdir(dirs[0]) if isfile(join(dirs[0], f))]
    test = [f for f in listdir(dirs[1]) if isfile(join(dirs[1], f))]
    train = [f for f in listdir(dirs[2]) if isfile(join(dirs[2], f))]

    dev = sorted(dev)
    test = sorted(test)
    train = sorted(train)

    with open(c.DATA_DIR+ "notes_dev_def.txt", "wb") as file:
        for item in dev:
            file.writelines(item + "\n")
    with open(c.DATA_DIR + "notes_test_def.txt", "wb") as file:
        for item in test:
            file.writelines(item + "\n")
    with open(c.DATA_DIR + "notes_train_def.txt", "wb") as file:
        for item in train:
            file.writelines(item + "\n")


if __name__ == '__main__':
    main([os.path.join(c.DATA_DIR, "notes_dev", ""), os.path.join(c.DATA_DIR, "notes_testing", ""), os.path.join(c.DATA_DIR, "notes_training", "")])
