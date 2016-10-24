import csv
import os

import re
import nltk
from fhcrc_clinical.SocialHistories.DataLoading import ServerQuery
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Document, Event, Patient, Sentence
from fhcrc_clinical.SocialHistories.SystemUtilities import Configuration
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *
from fhcrc_clinical.SocialHistories.Extraction.KeywordSearch import KeywordSearch
from os import listdir
from os.path import isfile, join
import sys

from fhcrc_clinical.parser import csv_parse


def main(environment, tsv_in=""):
    reload(sys)
    sys.setdefaultencoding('utf8')


    if environment == "Train":
        print "Loading data annotations from labkey server ..."
        annotation_metadata = ServerQuery.get_annotations_from_server()  # testing: stub data only

        print ("Loading split info ...")
        split_set = load_split_info(environment)

        print ("Loading labkey patients ...")
        labkey_training_patients = load_labkey_patients(annotation_metadata, split_set)

        # Temporary split of training data into test/train
        tmp_train_set, tmp_test_set = get_temporary_train_and_test_divisions(labkey_training_patients) # Necessary because we only have labeled training data at the moment
        print("\tLoaded " + str(len(tmp_train_set)) + " train patients (thats " + str(len(tmp_test_set)) + " saved for testing)")
        return tmp_train_set

    elif environment == "Test":
        print "Loading data annotations from labkey server ..."
        annotation_metadata = ServerQuery.get_annotations_from_server()  # testing: stub data only

        split_set = load_split_info("Train") # TODO: split should not be explicitly stated like this. It only is ATM b/c Labkey has no annotated testing data

        labkey_testing_patients = load_labkey_patients(annotation_metadata, split_set)
        # Temporary split of training data into test/train
        tmp_train_set, tmp_test_set = get_temporary_train_and_test_divisions(labkey_testing_patients) # Necessary because we only have labeled training data at the moment
        print("\tLoaded " + str(len(tmp_test_set)) + " test patients (thats " + str(len(tmp_train_set)) + " saved for training)")
        # for pat in tmp_test_set:
        #     print "\t" + str(pat.id)
        return tmp_test_set

    elif environment == "execute":
        print "Loading data from provided tsv file: " + tsv_in
        patients = build_patients_from_tsv(tsv_in)
        return patients


def get_temporary_train_and_test_divisions(patients):
    sorted_list = sorted(patients)
    doc_count = len(sorted_list)
    end_test_span = doc_count / 5  # the first 1/5 of the sorted data is the test_set
    test_span = (0, end_test_span)

    test_set = set()
    train_set = set()

    count = 0
    for doc in sorted_list:
        if count >= test_span[0] and count <= test_span[1]:
            test_set.add(doc)
        else:
            train_set.add(doc)
        count += 1
    return train_set, test_set


def load_split_info(environment):
    lines = list()
    if environment == "Test":
        with open(Configuration.DATA_DIR + "notes_dev_def.txt", "rb") as file:
            lines = file.read().splitlines()
    elif environment == "Train":
        with open(Configuration.DATA_DIR + "notes_train_def.txt", "rb") as file:
            lines = file.read().splitlines()
    return set(lines)


def load_labkey_patients(test_anns, split_set):
    # Load full data note repo from which TRAIN or TEST will pick and return a subset of docs
    print "\tLoading full data note repo ..."
    noteID_text_dict = load_data_repo(os.path.join(Configuration.DATA_DIR, "output"), split_set)
    print ("\tBuilding Patients from Labkey data ...")
    labkey_patients = build_patients_from_labkey(test_anns, noteID_text_dict, split_set)
    return labkey_patients


def get_doc_sentences(doc):
    # Split sentences
    split_sentences, sent_spans = split_doc_text(doc.text)

    # Create sentence objects and stuff into doc
    sentence_object_list = list()
    for sent, span in zip(split_sentences, sent_spans):
        sent_obj = Sentence(doc.id, sent, span[0], span[1])
        sentence_object_list.append(sent_obj)

    # Assign doc's keywords to appropriate sentences
    assign_keywords_to_sents(sentence_object_list, doc)
    return sentence_object_list


def split_doc_text(text):
    text = re.sub("\r", "", text)  # Carriage Returns are EVIL !!!!!
    sentences = nltk.tokenize.PunktSentenceTokenizer().sentences_from_text(text.encode("utf8"))
    spans = list(nltk.tokenize.PunktSentenceTokenizer().span_tokenize(text.encode("utf8")))

    #sentences, spans = split_by_double_newline(sentences, spans)
    sentences, spans = split_by_single_newlines(sentences, spans)
    sentences, spans = rejoin_sents_on_leading_punctuation(sentences, spans)

    return sentences, spans

def rejoin_sents_on_leading_punctuation(sentences, spans):
    # if a sentence ends in punctuation that implies related info in next sentence, append the next sentence to it, combine spans
    for i in range(len(sentences)):
        sent = sentences[i]
        if sent.rstrip().endswith(('?', ':', ';', '-')) or sent.istitle():
            if i + 1 < len(sentences):
                sentences[i] += " " + sentences[i + 1]
                spans[i] = (spans[i][0], spans[i + 1][1])
                sentences[i + 1] = " "
    return sentences, spans


def split_by_single_newlines(sentences, spans):
    final_sentences = []
    final_spans=[]
    for i in range(len(sentences)):
        sent = sentences[i]
        sents = sent.split('\n')
        span_split = get_spans_of_split_sent(sents, spans[i])
        final_spans.extend(span_split)
        final_sentences.extend(sents)
    return final_sentences, final_spans

def get_spans_of_split_sent(sent_list, span):
    spans = []
    count_begin = span[0]
    for sent in sent_list:
        count_end = count_begin + len(sent)
        spans.append((count_begin, count_end))
        count_end += 1
        count_begin = count_end
    return spans

def split_by_double_newline(sentences, spans):
    """ Take the sentences split by NLTK and further split them by double newline chars """
    split_sents = []
    split_spans = []

    for sent, span in zip(sentences, spans):
        doc_begin_index = span[0]
        nltk_sent_begin_index = 0
        chars = list(sent)

        # Find any splits in the sentences
        last_char = ""
        for nltk_sent_index, char in enumerate(chars):
            # Check for double newline
            doc_begin_index, nltk_sent_begin_index = check_for_double_newline(char, last_char, doc_begin_index,
                                                                              nltk_sent_index, nltk_sent_begin_index,
                                                                              chars, split_sents, split_spans)
            last_char = char

        # Add the last sent in the chunk
        doc_end_index = span[1]
        nltk_sent_index = len(chars)

        add_current_sent_and_span(doc_begin_index, doc_end_index, nltk_sent_begin_index, nltk_sent_index, chars,
                                  split_sents, split_spans)

    return split_sents, split_spans


def check_for_double_newline(char, last_char, doc_begin_index, nltk_sent_index, nltk_sent_begin_index, chars,
                             split_sents, split_spans):
    if char == '\n' and last_char == '\n':
        doc_end_index = doc_begin_index + nltk_sent_index - nltk_sent_begin_index
        add_current_sent_and_span(doc_begin_index, doc_end_index, nltk_sent_begin_index, nltk_sent_index, chars,
                                  split_sents, split_spans)

        nltk_sent_begin_index = nltk_sent_index + 1
        doc_begin_index = doc_end_index + 1

    return doc_begin_index, nltk_sent_begin_index


def add_current_sent_and_span(doc_begin_index, doc_end_index, nltk_sent_begin_index, nltk_sent_end_index,
                              chars, split_sents, split_spans):
    span = (doc_begin_index, doc_end_index)
    sent = "".join(chars[nltk_sent_begin_index:nltk_sent_end_index + 1])

    if sent:
        split_sents.append(sent)
        split_spans.append(span)

    # This is a dumb thing to handle the case that the doc ends with a double newline
    else:
        # Increment the end of the final span
        end_span_begin, end_span_end = split_spans[-1]
        del split_spans[-1]

        end_span_end += 1
        split_spans.append((end_span_begin, end_span_end))


def assign_goldLabels_to_sents(sents, doc):
    doc_gold_events = doc.gold_events
    for gold_event in doc_gold_events:
        if len(gold_event.status_spans) > 0:  # ie if it has a span and is not just a 'dummy' event
            for span in gold_event.status_spans:
                event_span_begin = span.start
                event_span_end = span.stop
                for sent in sents:
                    if event_span_begin > sent.span_in_doc_end:
                        # do nothing
                        tmp = 0
                    elif sent.span_in_doc_start > event_span_end:
                        break  # skip to the next event
                    else:
                        sent.gold_events.append(gold_event)
                        break  # skip to the next event
    pass


def assign_keywords_to_sents(sents, doc):
    """ Used for features in ML as well as assigning attributes to events """
    for event in doc.gold_events:
        substance = event.substance_type
        doc_hits = doc.keyword_hits[substance]
        keyword_index = 0
        sent_index = 0

        # Iterate through both sentences and keywords
        while not (keyword_index == len(doc_hits) or sent_index == len(sents)):
            sent_start = sents[sent_index].span_in_doc_start
            sent_end = sents[sent_index].span_in_doc_end
            keyword_start = doc_hits[keyword_index].span_start
            keyword_end = doc_hits[keyword_index].span_end

            # If current keyword is past current sentence, go to next sentence
            if keyword_start > sent_end:
                sent_index += 1
            # If sentence is past keyword, go to next keyword
            elif sent_start > keyword_end:
                keyword_index += 1
            # Else, they overlap and keyword should be assigned to sentence
            else:
                sents[sent_index].keyword_hits[substance].append(doc_hits[keyword_index])
                keyword_index += 1


def populate_event(doc, gold_label, substance, regex):
    event = Event(substance)

    event.status = gold_label.rstrip()
    if event.status != "":
        doc.gold_events.append(event)

    load_doc_keywords(doc, substance, regex)


def load_doc_keywords(doc, substance, regex):
    hits = KeywordSearch.find_doc_hits(doc, regex)
    doc.keyword_hits[substance].extend(hits)


def load_patient_labels(patient_gold_labels_path):
    pid_label = dict()
    if patient_gold_labels_path is not None:
        with open(patient_gold_labels_path, "rb") as file:
            lines = file.readlines()
        for line in lines:
            id_label = line.split()
            pid_label[id_label[0]] = id_label[1]
    return pid_label


def load_data_repo(NOTE_OUTPUT_DIR, doc_ids):
    id_text_dict = dict()
    all_notes = [f for f in listdir(NOTE_OUTPUT_DIR) if isfile(join(NOTE_OUTPUT_DIR, f))]
    for note in all_notes:
        if note in doc_ids:
            with open(os.path.join(NOTE_OUTPUT_DIR, note), "rb") as f:
                id_text_dict[note] = f.read()
    return id_text_dict


def get_labkey_documents(annId_patient_dict, docID_text_dict, split_set):
    annotater_ids = sorted(annId_patient_dict.keys())
    labkey_documents = list()
    for annotater_id in annotater_ids:
        patient_dict = annId_patient_dict[annotater_id]
        pat_ids = sorted(patient_dict.keys())
        for pat_id in pat_ids:
            docId_events = patient_dict[pat_id]  # {patientId : {eventType : EventObject}}
            for docId, event_dict in docId_events.iteritems():
                if docId in split_set:
                    doc_obj = Document(docId, docID_text_dict[docId])
                    # populate the docObj's event list
                    for type, event in event_dict.iteritems():
                        doc_obj.gold_events.append(event)
                    # split and assign document sentences from raw text
                    doc_obj.sent_list = get_doc_sentences(doc_obj)
                    labkey_documents.append(doc_obj)
                    # Match spans to sentence level
                    assign_goldLabels_to_sents(doc_obj.sent_list, doc_obj)

    return labkey_documents


def get_labkey_patients(labkey_documents):
    patients_dict = dict()
    patients_list = list()
    for doc in labkey_documents:
        patId = doc.id.split("_")[0]
        if patId not in patients_dict:
            patients_dict[patId] = list()
            patients_dict[patId].append(doc)
        else:
            patients_dict[patId].append(doc)

    for pid, doclist in patients_dict.iteritems():
        patient = Patient(pid)
        patient.doc_list = doclist
        patients_list.append(patient)
    return patients_list


def build_patients_from_labkey(annId_patient_dict, docID_text_dict, split_set):
    print("Building Labkey documents ...")
    labkey_documents = get_labkey_documents(annId_patient_dict, docID_text_dict, split_set)
    print("Building Labkey patients ...")
    labkey_patients = get_labkey_patients(labkey_documents)
    return labkey_patients


def build_patients_from_tsv(tsv_in):
    dict1, dict2 = csv_parse(tsv_in)
    patients = build_patients_from_csv_parse(dict1)
    return patients


def build_patients_from_csv_parse(patient_dict):
    patients = list()
    for patient_id, docs in patient_dict.iteritems():
        patient_documents, patient_caisis_id = get_patient_docs(docs)
        patient_obj = Patient(patient_caisis_id)
        patient_obj.doc_list = patient_documents
        patients.append(patient_obj)
    return patients


def get_patient_docs(docs):
    documents = list()
    patient_caisis_id = None
    for doc_id, fields in docs.iteritems():
        patient_caisis_id = doc_id.split('_')[0]
        sentence_objs, doc_text = get_sentences_from_field_tuples(fields, doc_id)
        sentence_objs = rejoin_sent_objs_on_leading_punctuation(sentence_objs)
        document_obj = Document(doc_id, doc_text)
        document_obj.sent_list = sentence_objs
        documents.append(document_obj)
    return documents, patient_caisis_id


def rejoin_sent_objs_on_leading_punctuation(sent_objs):
    new_sent_objs = []
    skip=False
    for i in range(len(sent_objs)):
        if skip:
            skip=False
        else:
            sent = sent_objs[i]
            if sent.text.rstrip().endswith(('?', ':', ';', '-')) or sent.text.istitle():
                if i + 1 < len(sent_objs):
                    new_text = sent_objs[i].text + " " + sent_objs[i+1].text
                    new_begin_span = sent_objs[i].span_in_doc_start
                    new_end_span = sent_objs[i+1].span_in_doc_end
                    #id_num, text, span_in_doc_start, span_in_doc_end
                    new_sent_obj = Sentence(sent.id,new_text, new_begin_span,new_end_span)
                    new_sent_objs.append(new_sent_obj)
                    skip=True
                else:
                    new_sent_objs.append(sent)
            else:
                new_sent_objs.append(sent)
    return new_sent_objs
    
def get_sentences_from_field_tuples(fields, doc_id):
    full_text = ""
    event_date = ""
    sentences = list()

    sorted_keys = sorted(fields.iteritems(), key=lambda x: x[0][2])

    for tup in sorted_keys:
        line=tup[1]
        if tup[0][1] == "FullText":
            full_text = line
        elif tup[0][1] == "EventDate":
            event_date = line
        else:
            # Assume the line is a sentence
            text_start_idx = tup[0][2]
            text_end_idx = len(line) + text_start_idx

            # Going off of the nlp engine's sentence segmentation is no good
            # split "lines" down into better sentences here, realign spans
            better_sentences, spans = split_doc_text(line)
            realigned_spans = list()
            for span in spans:
                realigned_spans.append((text_start_idx+span[0], text_start_idx+span[1]))

            for i in range(0,len(better_sentences), 1):
                text_start_idx = realigned_spans[i][0]
                text_end_idx = realigned_spans[i][1]
                sentence = Sentence(doc_id, better_sentences[i], text_start_idx, text_end_idx)
                sentences.append(sentence)

    return sentences, full_text


if __name__ == '__main__':
    main(Configuration.RUNTIME_ENV.TRAIN)
