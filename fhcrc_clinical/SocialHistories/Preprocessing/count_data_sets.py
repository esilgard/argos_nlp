import csv

# Clinic Type: Lung Cancer Early Detection and Prevention Clinic
import os

dev_in_dir = "/home/wlane/Documents/Substance_IE_Data/Docs_to_annotate/clean_dev/"
train_in_dir = "/home/wlane/Documents/Substance_IE_Data/Docs_to_annotate/train_original/"

in_dirs = [dev_in_dir, train_in_dir]
devset_count = 0
trainset_count = 0
for i in range(len(in_dirs)):
    for filename in os.listdir(in_dirs[i]):
        if os.path.isfile(os.path.join(in_dirs[i], filename)):
            print "opening file: " + str(os.path.join(in_dirs[i], filename))
            with open(os.path.join(in_dirs[i], filename), "rb") as tsvin:
                tsvin = csv.reader(tsvin, quoting=csv.QUOTE_ALL)
                for k, row in enumerate(tsvin):
                    if i==0:
                        devset_count +=1
                    else:
                        trainset_count +=1
print "TRAINING: " + str(trainset_count) + " documents."
print "DEV/TEST: " + str(devset_count) + " documents."
print "TOTAL DOCS: " + str(devset_count + trainset_count)
