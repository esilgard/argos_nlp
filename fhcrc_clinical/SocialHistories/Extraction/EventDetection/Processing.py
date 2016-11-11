import re
import os
import string
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import DATA_DIR
import json


def load_flor_patients():
    with open(os.path.join(DATA_DIR, "resources", "Florians_sentence_level_annotations", "sentence_level_annotations.json")) as data_file:
        data = json.load(data_file)
    return data


def flor_sentence_features_and_labels():
    doc_data = load_flor_patients()

    sent_feat_dicts = []  # List of sentence feature dictionaries
    labels_per_subst = {}  # Substance type : list of labels for each sentence (HAS/DOESN'T HAVE)

    for substance_type in SUBSTANCE_TYPES:
        labels_per_subst[substance_type] = []

    for doc in doc_data:
        for sent in doc_data[doc]:
            # Features per sentence
            sent_features = flor_get_features(sent["Sentence"].encode('utf-8'))
            sent_feat_dicts.append(sent_features)

            # Labels per sentences
            for substance_type in SUBSTANCE_TYPES:
                has_event = check_has_tob_event_flor(sent)
                if has_event and substance_type == "Tobacco": # Because Florian's data only labeled for Tobacco
                    labels_per_subst[substance_type].append(HAS_SUBSTANCE)
                else:
                    labels_per_subst[substance_type].append(NO_SUBSTANCE)

    return sent_feat_dicts, labels_per_subst

def sentence_features_and_labels(patients):
    """ Used for labelled data """
    sent_feat_dicts = []    # List of sentence feature dictionaries
    labels_per_subst = {}       # Substance type : list of labels for each sentence (HAS/DOESN'T HAVE)

    for substance_type in SUBSTANCE_TYPES:
        labels_per_subst[substance_type] = []

    # grab sentence features and labels
    count=0
    sent_count=0
    for patient in patients:
        for doc in patient.doc_list:
            for sent in doc.sent_list:
                if sent.text is not "":
                    sent_count += 1
                    # Features per sentence
                    sent_features = get_features(sent)
                    sent_feat_dicts.append(sent_features)

                    # Labels per sentences
                    for substance_type in SUBSTANCE_TYPES:
                        has_event = check_has_event_by_gold(substance_type, sent)
                        if has_event:
                            labels_per_subst[substance_type].append(HAS_SUBSTANCE)
                            count+=1
                        else:
                            labels_per_subst[substance_type].append(NO_SUBSTANCE)
    return sent_feat_dicts, labels_per_subst

def flor_get_features(sent_text):
    feats = {}
    # Unigrams
    grams = tokenize(sent_text)
    for gram in grams:
        feats[gram] = True
    return feats

def get_features(sent_obj):
    feats = {}
    # Unigrams
    grams = tokenize(sent_obj.text)
    for gram in grams:
        feats[gram] = True

    return feats


def tokenize(sent_text):
    sentence = sent_text.lower()
    grams = sentence.split()
    processed_grams = []

    left_omitted_chars = "|".join(["\$", "\."])
    right_omitted_chars = "|".join(["%"])
    ending_punc = re.sub(right_omitted_chars, "", string.punctuation)
    starting_punc = re.sub(left_omitted_chars, "", string.punctuation)

    for gram in grams:
        # Remove punctuation
        gram = gram.rstrip(ending_punc)
        gram = gram.lstrip(starting_punc)

        if gram:
            # Compress into word classes
            if gram.isdigit():
                processed_grams.append(NUMBER)
            elif re.sub("\.", "", gram).isdigit():
                processed_grams.append(DECIMAL)
            elif gram[0] == '$':
                processed_grams.append(MONEY)
            elif gram[len(gram) - 1] == '%':
                processed_grams.append(PERCENT)
            else:
                processed_grams.append(gram)

    return processed_grams

def check_has_tob_event_flor(sent):
    if sent["TobaccoStatus"] != "unknown":
        return True
    return False

def check_has_event_by_gold(substance_type, sent):
    """ Checks whether the sentence has an Event obj of the relevant subsType based on gold labels """
    if len(sent.gold_events) == 0:
        return False

    for event in sent.gold_events:
        if event.substance_type == substance_type and event.status_spans > 0:
            return True
    return False


def check_sent_highlight_overlap(substance_type, sent, highlighted_spans):
    sent_has_subst = False

    for gold_span in highlighted_spans[substance_type]:
        sent_has_subst = has_overlap(sent.span_in_doc_start, sent.span_in_doc_end,
                                     gold_span.start, gold_span.end)
        if sent_has_subst:
            break

    return sent_has_subst


def has_overlap(first_start, first_end, second_start, second_end):
    overlap = False
    # If first span is not completely before or after second span, there must be overlap
    if not (first_end <= second_start or first_start >= second_end):
        overlap = True
    return overlap
