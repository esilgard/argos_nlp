from sklearn.externals import joblib
import cPickle as Pickle

from SystemUtilities.Configuration import *
from Processing import *
from Extraction import Classification


def train_event_detectors(patients):

    # Retrieve features and labels per every sentence
    sent_feat_dicts, labels_per_subst = sentence_features_and_labels(patients)

    for substance_type in ML_CLASSIFIER_SUBSTANCES:
        # Train classifier
        classifier, feature_map = Classification.train_classifier(sent_feat_dicts, labels_per_subst[substance_type])

        # Save to file
        classf_file = MODEL_DIR + substance_type + EVENT_DETECT_MODEL_SUFFIX
        featmap_file = MODEL_DIR + substance_type + EVENT_DETECT_FEATMAP_SUFFIX

        joblib.dump(classifier, classf_file)
        Pickle.dump(feature_map, open(featmap_file, "wb"))
