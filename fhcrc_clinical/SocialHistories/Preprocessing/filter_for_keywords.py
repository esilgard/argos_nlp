# This script reads in a set of documents from a directory, and feeds them to KeywordHit module which checks
#    whether the document contains words of interest; anything related to smoking or tobacco.

from os import listdir
from os.path import isfile, join

import re

from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import *
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Document, Patient
from fhcrc_clinical.SocialHistories.Extraction.KeywordSearch import KeywordSearch
from nltk.tokenize import sent_tokenize
from fhcrc_clinical.SocialHistories.Preprocessing.get_docs_to_annotate import DataSplitter


def main():
    # Determine environment. This script will only produce filtered tsv files for the appropriate environment
    data_src = ""
    split = ""
    if ENV == RUNTIME_ENV.TRAIN:
        data_src = TRAIN_SPLIT_DIR
        split = "train"
    if ENV == RUNTIME_ENV.EXECUTE:
        data_src = DEV_SPLIT_DIR
        split = "dev"

    # Read in from folder containing all available data
    data = load_data(data_src)
    documents = create_documents_from_data(data)
    patients = create_patients_from_documents(documents)

    print("Searching documents for keywords...")
    docs_with_keywords = KeywordSearch.search_keywords(patients)

    # Filter out duplicate text spans
    print("Filtering out documents with duplicate text spans whose context is also redundant ...")
    docs_with_keywords = filter_out_texts_with_duplicate_keyword_hit_and_context(docs_with_keywords)

    # sort document objs based on id
    docs_with_keywords_list = list(docs_with_keywords)
    docs_with_keywords_list.sort(key=lambda x: x.id)

    # Based on Flor's divisions, derive list of documents that need annotation
    print("Generating list of documents that need annotations...")
    splitter = DataSplitter(docs_with_keywords_list)
    splitter.write_notes_needing_annotation(split)
    print("Done.")


def load_data(data_src):
    print("Loading data...")
    # debug
    # data_src = "C:\Users\sdmorris\Documents\FHCRC\ExposureProject\Substance_IE_Data\mini_data.nlp"
    # data_src = "C:\Users\wlane\Documents\Substance_IE_Data\mini_output_corpus"
    # end debug

    file_list = [f for f in listdir(data_src) if isfile(join(data_src, f))]
    id_and_note = dict()
    for file in file_list:
        full_id = file
        with open(data_src + "/" + file) as f:
            content = f.read()
            id_and_note[full_id] = content
    return id_and_note  # returns dictionary of {doc_id : document_text}


def create_documents_from_data(data):
    print("Creating Documents from data...")
    documents = list()

    data_keys = sorted(data.keys())
    for key in data_keys:
        id = key
        text = data[key]
        new_doc = Document(id, text)
        sent_tokenize_list = sent_tokenize(text.decode("utf-8"))
        new_doc.sent_list = sent_tokenize_list
        documents.append(new_doc)
    return documents


def create_patients_from_documents(documents):
    print ("Creating patients from documents...")
    patientId_docList = dict()
    for doc in documents:
        patient_id = doc.id.split("_")[0]
        if patient_id not in patientId_docList:
            patientId_docList[patient_id] = list()
        patientId_docList[patient_id].append(doc)

    # read through patients in dictionary and make patient objects for each
    patients = list()
    patient_id_keys = sorted(patientId_docList.keys())
    for id in patient_id_keys:
        doc_list = patientId_docList[id]
        new_patient = Patient(id)
        new_patient.doc_list = doc_list
        patients.append(new_patient)
    return patients


def get_sent_start_stop_idx(text, idx_b, idx_e):
    sent_start = idx_b
    sent_end = idx_e

    while text[sent_start] not in {"\n", ".", "!", "?"}:
        sent_start -= 1
    while text[sent_end] not in {"\n", ".", "!", "?"}:
        sent_end += 1
        if text[sent_end] == "?":
            sent_end += 2
    return sent_start, sent_end


def are_equal(list_of_texts, text2,
              hits): # right now, equality is defined as all matches' contexts (up to punctuation or \n) being identical
    for text1 in list_of_texts:
        matched_hit = 0
        for hit in hits:
            pattern = text2[hit.span_start:hit.span_end]
            p = re.compile(pattern)
            m = re.findall(pattern, text1)
            s = p.search(text1)
            if len(m) == 0:  # If there is no match, then t2 has a hit t1 doesnt. We want to skip to comparing next doc
                break

            span = s.span()

            t1_idx_b = span[0]
            t1_idx_e = span[1]
            t2_idx_b = hit.span_start
            t2_idx_e = hit.span_end
            sent1_start_idx, sent1_end_idx = get_sent_start_stop_idx(text1, t1_idx_b, t1_idx_e)
            sent2_start_idx, sent2_end_idx = get_sent_start_stop_idx(text2, t2_idx_b, t2_idx_e)

            text1_substr = text1[sent1_start_idx:sent1_end_idx]
            text2_substr = text2[sent2_start_idx:sent2_end_idx]
            if text1_substr == text2_substr:
                print "matched sents: " + text1[sent1_start_idx:sent1_end_idx] + " and " + text2[
                                                                                           sent2_start_idx:sent2_end_idx]
                matched_hit += len(m)
        if matched_hit ==len(hits):
            return True
    return False


def get_hash(thetuple, doc):
    # hash= str(len(thetuple))+doc.id.split("_")[0] # the # of keyword matches

    # for item in thetuple:
    #     hash+=str(item.text)+doc.id.split("_")[0] #str(item.span_end)+str(item.span_start)+

    hash = doc.id.split("_")[0]
    return hash


def filter_by_type(TYPE, doc, docs_to_keep, keywordList_text):
    thetuple = tuple(doc.keyword_hits[TYPE])
    hash = get_hash(thetuple, doc)

    if "102515_103" in doc.id: #108, 106
        pause =9
    if "102515_106" in doc.id:  # 108, 106
        pause = 9
    if "102515_108" in doc.id:  # 108, 106
        pause = 9

    if hash not in keywordList_text and len(doc.keyword_hits[TYPE]) != 0:
        docs_to_keep.add(doc)
        keywordList_text[hash] = list()
        keywordList_text[hash].append(doc.text)
        # keywordList_text[hash] = doc.text
    elif len(doc.keyword_hits[TYPE]) != 0:
        they_are = are_equal(keywordList_text[hash], doc.text, doc.keyword_hits[TYPE])
        if not they_are:
            docs_to_keep.add(doc)
            keywordList_text[hash].append(doc.text)
            # keywordList_text[hash] = doc.text
    pass


def filter_out_texts_with_duplicate_keyword_hit_and_context(docs_with_keywords):
    # sort document objs based on id
    docs_with_keywords_list = list(docs_with_keywords)
    docs_with_keywords_list.sort(key=lambda x: x.id)

    docs_to_keep = set()
    keywordList_text = dict()
    for doc in docs_with_keywords_list:
        filter_by_type(ALCOHOL, doc, docs_to_keep, keywordList_text)
        filter_by_type(TOBACCO, doc, docs_to_keep, keywordList_text)
    return docs_to_keep


if __name__ == '__main__':
    main()
