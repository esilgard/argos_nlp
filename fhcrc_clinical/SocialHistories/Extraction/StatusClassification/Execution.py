import cPickle as Pickle
from sklearn.externals import joblib
import numpy as np

from fhcrc_clinical.SocialHistories.Extraction.StatusClassification.Shared_Processing import get_feature_vectors
from fhcrc_clinical.SocialHistories.SystemUtilities import Debugger
from fhcrc_clinical.SocialHistories.Extraction import Classification
from fhcrc_clinical.SocialHistories.Extraction.Classification import vectorize_sentence, classify_many_instances
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import *
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *


def classify_sentence_status(sentences):

    for event_type in SUBSTANCE_TYPES:
        # load classifiers and feature map
        classifier, feature_map = load_classifier(event_type)

        # extract features
        feature_vectors = get_feature_vectors(sentences)

        # classify sentences
        classifications = classify_many_instances(classifier, feature_map, feature_vectors)

        # assign classification directly to the sentence
        for i in range(0, len(sentences), 1):
            sent = sentences[i]
            for event in sent.predicted_events:
                if event.substance_type == event_type:
                    event.status = classifications[i]

        # DEBUG
        Debugger.print_status_classification_results(sentences, classifications, event_type)
        # end DEBUG
    pass


def load_classifier(event_type):
    classifier_file = os.path.join(MODEL_DIR, event_type+ STATUS_CLASSF_MODEL_SUFFIX)
    feature_map_file = os.path.join(MODEL_DIR, event_type+ STATUS_CLASSF_FEATMAP_SUFFIX)

    classifier, feature_map = Classification.load_classifier(classifier_file, feature_map_file)

    return classifier, feature_map
