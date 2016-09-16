import re

import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c
import fhcrc_clinical.SocialHistories.SystemUtilities.Globals as g
import os
import openpyxl
import collections
import csv

from fhcrc_clinical.SocialHistories.Preprocessing import *
from fhcrc_clinical.SocialHistories.Preprocessing.CSVBatch import CSVBatch


def write_unannotated_info_to_file(unannotated_documents):
    with open(c.SUBSTANCE_IE_DATA_FOLDER + "docs_to_annotate.txt", "w") as f:
        for doc in unannotated_documents:
            f.write(doc.id + "\n")
    print("List of documents to annotate written to: " + c.SUBSTANCE_IE_DATA_FOLDER + "docs_to_annotate.txt")
    pass


def get_metadata_dict():
    metadata = dict()
    with open(c.SUBSTANCE_IE_DATA_FOLDER + "marvelously_massive_metadata_muniments_dict.txt", "rb") as f:
        lines = f.readlines()
    for line in lines:
        items = line.split()
        caisis_docid = items[0]
        mrn = items[1]
        timestamp = items[2]
        metadata[caisis_docid] = (mrn, timestamp)
    return metadata


def is_it_discharge_instructions(doc):
    """The definition of what a discharge instruction looks like could be different in another data set."""
    split_text = doc.text.split("\n")

    # Check first 4 lines for patient discharge instructions because we really really dont want any of those
    if len(split_text) > 4:
        # p = re.compile(text2[hit.span_start:hit.span_end])
        # m = p.search(text1)
        # span = m.span()
        p = re.compile("assessment", re.IGNORECASE)
        if p.match(split_text[0]):
            return True

        if "Discharge Instruction" in split_text[0] or \
                        "Discharge Instruction" in split_text[1] or \
                        "Discharge Instruction" in split_text[2] or \
                        "Discharge Instruction" in split_text[3]:
            return True
        if "Discharge Summary" in split_text[0] or \
                        "Discharge Summary" in split_text[1] or \
                        "Discharge Summary" in split_text[2] or \
                        "Discharge Summary" in split_text[3]:
            return True
        if "DISCHARGE SUMMARY" in split_text[0] or \
                        "DISCHARGE SUMMARY" in split_text[1] or \
                        "DISCHARGE SUMMARY" in split_text[2] or \
                        "DISCHARGE SUMMARY" in split_text[3]:
            return True
    return False


def get_batches(documents_needing_annotation):
    total_doc_count = 0
    count = 0
    batch_num = 0
    BATCH_SIZE = 99
    batches = list()
    for doc in documents_needing_annotation:
        # make sure its not a Discharge Instructions doc: we don't need those
        is_discharge_doc = is_it_discharge_instructions(doc)

        if not is_discharge_doc:
            total_doc_count += 1
            if count == 0:
                batch = CSVBatch(batch_num)
                batch_num += 1
                batch.add_document(doc)
                if count == BATCH_SIZE or total_doc_count == len(documents_needing_annotation)-1:
                    batches.append(batch)
                    count = -1
            elif count == BATCH_SIZE or total_doc_count == len(documents_needing_annotation)-1:
                batch.add_document(doc)
                batches.append(batch)
                count = -1
            else:
                batch.add_document(doc)
            count += 1
    return batches


def write_docs_needing_annotation_to_csv_batches(documents_needing_annotation, split):
    # Sort notes into batches of 100
    batches = get_batches(documents_needing_annotation)
    metadata_dict = get_metadata_dict()
    for batch in batches:
        with open(c.DOCS_NEEDING_ANNOTATION_DIR +"\\"+split+"\\"+ "annotation_batch_" + str(batch.id) + ".nlp.tsv", "wb") as csvfile:
            batch_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            batch_writer.writerow(["MRN", "FillerOrderNo", "EventDate", "ObservationValue"])
            for document in batch.documents:
                id = document.id.replace("-", "_")
                mrn = metadata_dict[id][0]
                timestamp = metadata_dict[id][1]
                batch_writer.writerow([mrn, id, timestamp, document.text])
    print("tsv batch files ready for annotation written to: " + c.DOCS_NEEDING_ANNOTATION_DIR)
    pass



class DataSplitter:
    def __init__(self, docs_with_keywords):
        self.docs_with_keywords_list = docs_with_keywords
        self.doc_test_dict = dict()
        self.doc_dev_dict = dict()
        self.doc_train_dict = dict()
        self.patients_test_dict = dict()
        self.patients_dev_dict = dict()
        self.patients_train_dict = dict()

    def write_notes_needing_annotation(self, split):
        self.get_splits(split)
        pass

    def get_unannotated_documents(self, all_keyword_documents):
        unannotated_docs = list()
        for doc in all_keyword_documents:
            doc.id = doc.id.replace("_", "-")  # Our ids have '_', Flors have '-'
            if not doc.id in self.doc_test_dict.keys() \
                    and not doc.id in self.doc_dev_dict.keys() \
                    and not doc.id in self.doc_train_dict.keys():
                unannotated_docs.append(doc)
        return unannotated_docs

    def get_list_of_documents_to_annotate(self):
        # all of the .self attributes have been populated by this point, use them to sort the new data

        unannotated_documents = self.get_unannotated_documents(self.docs_with_keywords_list)
        return unannotated_documents

    def populate_dir_dict(self, doc_dict, patients_dict, dirs):
        doc_gold_dir = dirs[0]
        patients_gold_dir = dirs[1]

        with open(doc_gold_dir) as d:
            lines = d.readlines()
        for line in lines:
            id_label = line.split()
            id = id_label[0]
            label = id_label[1]
            doc_dict[id] = label

        with open(patients_gold_dir) as d:
            lines = d.readlines()
        for line in lines:
            id_label = line.split()
            id = id_label[0]
            label = id_label[1]
            patients_dict[id] = label
        pass

    def split_by_flor(self, documents_needing_annotation, wanted_dict, unwanted1, unwanted2):
        docs_belonging_to_relevant_split = list()
        unclaimed = list()
        for doc in documents_needing_annotation:
            id = doc.id.split('_')[0]
            id = id.split('-')[0]
            if id in wanted_dict:
                docs_belonging_to_relevant_split.append(doc)
            elif id not in unwanted1 and id not in unwanted2:
                unclaimed.append(doc)

        return docs_belonging_to_relevant_split

    def get_splits(self, split):
        doc_dev_gold_dir = c.doc_dev_gold_dir
        doc_test_gold_dir = c.doc_test_gold_dir
        doc_train_gold_dir = c.doc_train_gold_dir
        patients_test_gold_dir = c.patients_test_gold_dir
        patients_train_gold_dir = c.patients_train_gold_dir
        patients_dev_gold_dir = c.patients_dev_gold_dir

        dev_dirs = [doc_dev_gold_dir, patients_dev_gold_dir]
        test_dirs = [doc_test_gold_dir, patients_test_gold_dir]
        train_dirs = [doc_train_gold_dir, patients_train_gold_dir]

        self.populate_dir_dict(self.doc_dev_dict, self.patients_dev_dict, dev_dirs)
        self.populate_dir_dict(self.doc_test_dict, self.patients_test_dict, test_dirs)
        self.populate_dir_dict(self.doc_train_dict, self.patients_train_dict, train_dirs)

        documents_needing_annotation = self.get_list_of_documents_to_annotate()
        write_unannotated_info_to_file(documents_needing_annotation)



        write_docs_needing_annotation_to_csv_batches(documents_needing_annotation, split)
