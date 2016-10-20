from sklearn.externals import joblib
import cPickle as Pickle
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import *
from Processing import *
from fhcrc_clinical.SocialHistories.Extraction import Classification


def train_event_detectors(patients):
    # Retrieve features and labels per every sentence
    sent_feat_dicts, labels_per_subst = sentence_features_and_labels(patients)

    print "Training event detection on " + str(len(sent_feat_dicts)) + " sents total"

    # Get Florian's data to reinforce training
    flor_sent_feat_dicts, flor_labels_per_subst = flor_sentence_features_and_labels()
    sent_feat_dicts.extend(flor_sent_feat_dicts)
    labels_per_subst["Tobacco"].extend(flor_labels_per_subst["Tobacco"])
    labels_per_subst["Alcohol"].extend(flor_labels_per_subst["Alcohol"])

    for substance_type in ML_CLASSIFIER_SUBSTANCES:
        # Train classifier
        classifier, feature_map = Classification.train_classifier(sent_feat_dicts, labels_per_subst[substance_type])

        # Save to file
        classf_file = os.path.join(MODEL_DIR, substance_type + EVENT_DETECT_MODEL_SUFFIX)
        featmap_file = os.path.join(MODEL_DIR, substance_type + EVENT_DETECT_FEATMAP_SUFFIX)
        joblib.dump(classifier, classf_file)
        Pickle.dump(feature_map, open(featmap_file, "wb"))
