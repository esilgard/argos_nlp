from sklearn.externals import joblib
import cPickle as Pickle
from SystemUtilities.Configuration import *
from Extraction import Classification
import Processing


def train_event_fillers(patients):
    # Train model
    features, labels = Processing.features_and_labels(patients)
    classifier, feature_map = Classification.train_classifier(features, labels)

    # Write models to file
    classf_file = MODEL_DIR + EVENT_FILLER_MODEL_NAME
    featmap_file = MODEL_DIR + EVENT_FILLER_FEATMAP_NAME

    joblib.dump(classifier, classf_file)
    Pickle.dump(feature_map, open(featmap_file, "wb"))
