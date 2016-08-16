""" This script takes Florian's keyword-filtered texts and writes them as tsv files in a given directory """
import csv
from os import listdir
from os.path import isfile, join
import SystemUtilities.Configuration as c


def get_splits():
    # read in the different split lists
    with open(c.doc_dev_gold_dir,"rb") as dev:
        devlines = dev.readlines()
    with open(c.doc_train_gold_dir, "rb") as train:
        trainlines = train.readlines()
    with open(c.doc_test_gold_dir, "rb") as test:
        testlines = test.readlines()
    return trainlines, testlines, devlines


def write_split(splitname, doc_ids, id_text):
    with open(r"C:\Users\wlane\Documents\Substance_IE_Data\FLOR_filtered_tsv\flor_" + splitname + ".csv",
              "wb") as csvfile:
        batch_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        batch_writer.writerow(["ID", "TEXT", "TOB_GOLD_LABEL", "ALC_GOLD_LABEL"])
        for id_annotation in doc_ids:
            id = id_annotation.split("\t")[0]
            tobacco_annotation = id_annotation.split("\t")[1]
            alc_annotation = "UNKNOWN" # UNKNOWN here is the alcohol status. Flor's docs dont annotate for this
                                       # But we still need to populate the field because the DataLoader expects it
            batch_writer.writerow([id, id_text[id], tobacco_annotation, alc_annotation])
    pass


def write_csv(id_text):
    train, test, dev = get_splits()
    write_split("train", train, id_text)
    write_split("dev", dev, id_text)
    write_split("test", test, id_text)
    pass


def get_doc_ids():
    with open(c.doc_all_gold_dir, "rb") as file:
        doc_ids = file.readlines()
    return doc_ids


def build_dict_of_id_text():
    mypath = "C:\\Users\\wlane\\Documents\\Florian_smoking\smoking_status\\full_data_set"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    id_text = dict()
    for f in onlyfiles:
        with open(mypath + "\\" + f, "rb") as doc:
            lines = doc.read()
            id_text[f] = lines
    return id_text


def main():
    id_text_dict = build_dict_of_id_text()
    write_csv(id_text_dict)


if __name__ == '__main__':
    main()
