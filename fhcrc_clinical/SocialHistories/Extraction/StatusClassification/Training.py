import cPickle as Pickle

import re
from sklearn.externals import joblib
import os

from fhcrc_clinical.SocialHistories.Extraction.Classification import train_classifier
from fhcrc_clinical.SocialHistories.Extraction.EventDetection.Processing import flor_sentence_features_and_labels, load_flor_patients
from fhcrc_clinical.SocialHistories.Extraction.StatusClassification.Shared_Processing import get_bigrams, \
    get_feature_vectors, flor_get_feature_vectors
from fhcrc_clinical.SocialHistories.SystemUtilities import Globals
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import MODEL_DIR
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import STATUS_CLASSF_FEATMAP_SUFFIX, STATUS_CLASSF_MODEL_SUFFIX, \
    SUBSTANCE_TYPES, TOBACCO


def train_status_classifier(patients):
    sentences = get_sentences_from_patients(patients)
    # Load Florian data
    flor_tbc_feats, flor_tbc_labels = flor_get_feature_vectors()
    for subs_type in SUBSTANCE_TYPES:
        # Create Feature-Label pairs for each Subs Abuse type
        feats = get_feature_vectors(sentences)
        labels = get_labels(sentences, subs_type)
        if subs_type == TOBACCO:
            # Join flor's tobacco features and labels to regular tobacco features and labels
            feats.extend(flor_tbc_feats)
            labels.extend(flor_tbc_labels)
            
        # Create Model
        print("Training Status Classifier on " + str(len(feats)) + " sentences")
        classifier, feature_map = train_classifier(feats, labels)
        # Set output directory pointers for model files
        classf_file = os.path.join(MODEL_DIR, subs_type + STATUS_CLASSF_MODEL_SUFFIX)
        featmap_file = os.path.join(MODEL_DIR, subs_type + STATUS_CLASSF_FEATMAP_SUFFIX)
        #Write models file
        joblib.dump(classifier, classf_file)
        Pickle.dump(feature_map, open(featmap_file, "wb"))
    pass

    
def get_sentences_from_patients(patients):
    sentences = list()
    for patient in patients:
        for document in patient.doc_list:
            for sent_obj in document.sent_list:
                if (len(sent_obj.gold_events)) > 0: # if the sentence has an event
                    sentences.append(sent_obj)
    return sentences


def get_labels(sents, subs_type):
    labels = list()
    for sent in sents:
        label, evidence = sent.get_status_label_and_evidence(subs_type)
        labels.append(label)
    return labels