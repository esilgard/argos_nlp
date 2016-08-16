import SystemUtilities.Configuration as c
import SystemUtilities.Globals as g
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

    with open(c.data_dir+"notes_dev_def.txt", "wb") as file:
        for item in dev:
            file.writelines(item + "\n")
    with open(c.data_dir + "notes_test_def.txt", "wb") as file:
        for item in test:
            file.writelines(item + "\n")
    with open(c.data_dir + "notes_train_def.txt", "wb") as file:
        for item in train:
            file.writelines(item + "\n")


if __name__ == '__main__':
    main([c.DEV_SPLIT_DIR, c.TEST_SPLIT_DIR, c.TRAIN_SPLIT_DIR])
