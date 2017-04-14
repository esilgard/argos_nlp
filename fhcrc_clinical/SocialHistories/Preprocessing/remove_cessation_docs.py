import csv

# Clinic Type: Lung Cancer Early Detection and Prevention Clinic
import os

dev_out_dir = "/home/wlane/Documents/Substance_IE_Data/Docs_to_annotate/clean_dev/"
train_out_dir = "/home/wlane/Documents/Substance_IE_Data/Docs_to_annotate/clean_train/"
dev_in_dir = "/home/wlane/Documents/Substance_IE_Data/Docs_to_annotate/dev/"
train_in_dir = "/home/wlane/Documents/Substance_IE_Data/Docs_to_annotate/train/"

in_dirs = [dev_in_dir, train_in_dir]
out_dirs = [dev_out_dir, train_out_dir]

for i in range(len(in_dirs)-1):
    for filename in os.listdir(in_dirs[i]):
        if os.path.isfile(os.path.join(in_dirs[i], filename)):
            print "opening file: " + str(os.path.join(in_dirs[i], filename))
            with open(os.path.join(in_dirs[i], filename), "rb") as tsvin, open(os.path.join(out_dirs[i], filename), "wb") as tsvout:
                tsvin = csv.reader(tsvin, quoting=csv.QUOTE_ALL)
                tsvout = csv.writer(tsvout)
                rows_to_write = list()
                for k, row in enumerate(tsvin):
                    skip = False
                    print '\tline[{}] = {}'.format(k, row)
                    text = row[3].split("\n")
                    for j in range(4):
                        if j >= len(text):
                            break
                        if "Clinic Type: Lung Cancer Early Detection and Prevention Clinic." in text[j]:
                            print "\t ^skip this mf"
                            skip=True
                    if not skip:
                        # tsvout.writerows(tsvin)
                        rows_to_write.append(row)
                tsvout.writerows(rows_to_write)
