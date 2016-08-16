import cPickle as Pickle
from sklearn.externals import joblib
import numpy as np

from Extraction import Classification
from Extraction.Classification import vectorize_sentence, classify_many_instances
from SystemUtilities.Configuration import MODEL_DIR, EVENT_DETECT_MODEL_SUFFIX, EVENT_DETECT_FEATMAP_SUFFIX, \
    STATUS_CLASSF_FEATMAP_SUFFIX, STATUS_CLASSF_MODEL_SUFFIX, SUBSTANCE_TYPES


def classify_sentence_status(sentences):

    for event_type in SUBSTANCE_TYPES:
        # load classifiers and feature map
        classifier, feature_map = load_classifier(event_type)

        # extract features
        features = extract_features(sentences)

        classifications = classify_many_instances(classifier, feature_map, features)

        # assign classification directly to the sentence
        for i in range(0, len(sentences), 1):
            sent = sentences[i]
            for event in sent.predicted_events:
                if event.substance_type == event_type:
                    event.status = classifications[i]
    pass


def load_classifier(event_type):
    classifier_file = MODEL_DIR + event_type + STATUS_CLASSF_MODEL_SUFFIX
    feature_map_file = MODEL_DIR + event_type + STATUS_CLASSF_FEATMAP_SUFFIX

    classifier, feature_map = Classification.load_classifier(classifier_file, feature_map_file)

    return classifier, feature_map


def extract_features(sents):
    feature_vecs = list()
    for sent in sents:
        vector = dict()
        input_list = sent.text.lower().rstrip(",.!?:;").split()
        some_bigrams = list(get_bigrams(input_list))

        for pair in some_bigrams:
            vector[pair[0] + "_" + pair[1]] = True
        for x in input_list:
            vector[x] = True

        feature_vecs.append(vector)
    return feature_vecs


def get_bigrams(input_list):
    return zip(input_list, input_list[1:])