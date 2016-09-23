import os
import re
from nltk import StanfordNERTagger

from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Attribute
from fhcrc_clinical.SocialHistories.SystemUtilities import Globals
from fhcrc_clinical.SocialHistories.Extraction.AttributeExtraction.SentenceTokenizer import strip_sec_headers_tokenized_text
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import ATTRIB_EXTRACTION_DIR_HOME, STANFORD_NER_PATH, DATA_DIR
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import entity_types


def extract(patients, model_path=ATTRIB_EXTRACTION_DIR_HOME,
         stanford_ner_path=STANFORD_NER_PATH):

    # Extract all sentences with subs info + the sentence after
    all_sentences = get_sentences_with_info_plus_sentence_after(patients)

    for type in entity_types: # {Amount, Duration, QuiteDate, TimeAgo, QuitAge, SecondhandAmount}

        #TODO: alternatively classify all sentences at once? is it faster?
        model_name = model_path + "Models/" + "model-" + type + ".ser.gz"
        #classify_sentences(all_sentences, model_name, stanford_ner_path, type)

        for sentobj in all_sentences:
            test_model_in_mem(stanford_ner_path, model_name, sentobj, type)
    print("Finished CRF classification")


def get_sentences_containing_info_type(sentences_with_info):
    #Initialize dictionary
    sentences_by_abuse_type = dict()
    for subs_type in Globals.ML_CLASSIFIER_SUBSTANCES:
        sentences_by_abuse_type[subs_type] = list()

    for sent in sentences_with_info:
        for event in sent.predicted_events:
            sentences_by_abuse_type[event.substance_type].append(sent)
    return sentences_by_abuse_type


def tokenize_sentence(sent_obj):
    text = sent_obj.text
    tokenized_text = list()
    spans = list()

    # Recover spans here
    for match in re.finditer("\S+", text):
        start = match.start()
        end = match.end()
        word = match.group(0)
        tokenized_text.append(word.rstrip(",.;:)("))
        spans.append((start, end))
    tokenized_text = strip_sec_headers_tokenized_text(tokenized_text)
    return tokenized_text


def write_crf_classified_stuff_to_file(tokd_sentences, classified_text, type):
    with open(os.path.join(DATA_DIR, "DebugOutputs", "attrib_extr_tokd_sentences_"+type+"_DEBUG.txt"), "wb") as file:
        for sent in tokd_sentences:
            file.write(str(sent)+"\n")
    with open(os.path.join(DATA_DIR, "DebugOutputs", "attrib_extr_clssfd_sentences_"+type +"_DEBUG.txt"), "wb") as file:
        for sent in classified_text:
            file.write(str(sent)+"\n")
    pass


def add_period_to_each_sentence(tokd_sentences):
    for sent_list in tokd_sentences:
        sent_list.append('.')
    return tokd_sentences


def classify_sentences(all_sentences, model_name, stanford_ner_path, type):
    print("\tClassifying " + type + " attributes..")
    stanford_tagger = StanfordNERTagger(
        model_name,
        stanford_ner_path,
        encoding='utf-8')

    tokd_sentences = []
    for sent in all_sentences:
        tokenized_text = tokenize_sentence(sent)
        tokd_sentences.append(tokenized_text)

    classified_text = stanford_tagger.tag_sents(tokd_sentences)

    # DEBUG
    write_crf_classified_stuff_to_file(tokd_sentences, classified_text, type)
    # end DEBUG
    tmp=0

    pass


def test_model_in_mem(stanford_ner_path, model_name, sent_obj, type):
    stanford_tagger = StanfordNERTagger(
        model_name,
        stanford_ner_path,
        encoding='utf-8')

    text = sent_obj.text
    tokenized_text = list()
    spans = list()

    #Recover spans here
    for match in re.finditer("\S+", text):
        start = match.start()
        end = match.end()
        word = match.group(0)
        tokenized_text.append(word.rstrip(",.;:)("))
        spans.append((start,end))
    tokenized_text = strip_sec_headers_tokenized_text(tokenized_text)
    classified_text = stanford_tagger.tag(tokenized_text)


    # Expand tuple to have span as well
    len_diff = len(spans) - len(classified_text) #Headers were stripped, so if this occured in the previous step, we have t account for the offset
    final_class_and_span = list()
    for idx,tup in enumerate(classified_text):
        combined = (classified_text[idx][0],classified_text[idx][1],spans[idx+len_diff][0],spans[idx+len_diff][1])
        final_class_and_span.append(combined)

    # print(classified_text)
    sent_obj.sentence_attribs.extend(get_attributes(final_class_and_span))
    return sent_obj


def get_attributes(crf_classification_tuple_list):
    attribs = list()
    i = 0
    while i < len(crf_classification_tuple_list)-1:
        crf_classification_tuple = crf_classification_tuple_list[i]
        classL = crf_classification_tuple[1]
        start = crf_classification_tuple[2]
        if classL != "0": # beginning of a labeled span
            full_begin_span = start
            full_end_span = start
            full_text = ""
            while i < len(crf_classification_tuple_list)-1 and classL == crf_classification_tuple_list[i][1]:
                crf_classification_tuple = crf_classification_tuple_list[i]
                full_text += crf_classification_tuple[0] + " "
                full_end_span = crf_classification_tuple[3]
                i += 1
            attrib = Attribute(classL, full_begin_span, full_end_span, full_text)
            attribs.append(attrib)
        i += 1
    return attribs

def get_sentences_with_info_plus_sentence_after(patients):
    all_sents = list()
    for patient in patients:
        for document in patient.doc_list:
            grab_next = False
            for sentence in document.sent_list:
                if len(sentence.predicted_events) > 0 or grab_next:
                    if grab_next:
                        grab_next = False
                    if len(sentence.predicted_events) > 0:
                        grab_next = True
                    all_sents.append(sentence)
    return all_sents