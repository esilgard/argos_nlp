from fhcrc_clinical.SocialHistories.Extraction.KeywordSearch import KeywordSearch
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import *
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Event
from Processing import *
from fhcrc_clinical.SocialHistories.Extraction import Classification


# Add sentence-level predicted events in Patient object
def detect_sentence_events(patients):
    # store all sentences which have events. This is used as input to StatusClassification
    sentences_predicted_to_have_events = list()

    # Substances detected with ML classifier
    for substance_type in ML_CLASSIFIER_SUBSTANCES:
        classifier, feature_map = load_event_classifier(substance_type)

        for patient in patients:
            for doc in patient.doc_list:
                for sent in doc.sent_list:
                    # block out subs sentences with regex first, because vectorization is expensive
                    if rgx_match_substance_reference(sent):
                        classify_sent_for_substance(classifier, feature_map, sent, substance_type,
                                                    sentences_predicted_to_have_events)

    return sentences_predicted_to_have_events


def load_event_classifier(event_type):
    classifier_file = os.path.join(MODEL_DIR, event_type + EVENT_DETECT_MODEL_SUFFIX)
    print("\tClassifier File at: " + os.path.join(MODEL_DIR, event_type + EVENT_DETECT_MODEL_SUFFIX))
    feature_map_file = os.path.join(MODEL_DIR, event_type + EVENT_DETECT_FEATMAP_SUFFIX)
    print("\tFeatMap File at: " + os.path.join(MODEL_DIR, event_type + EVENT_DETECT_FEATMAP_SUFFIX))

    classifier, feature_map = Classification.load_classifier(classifier_file, feature_map_file)
    return classifier, feature_map


def classify_sent_for_substance(classifier, feature_map, sent, substance, sentences_predicted_to_have_events):
    # USE THE SVM:
    sent_feats = get_features(sent)
    classifications = Classification.classify_instance(classifier, feature_map, sent_feats)
    # Add detected event to sentence
    if classifications[0] == HAS_SUBSTANCE:
        event = Event(substance)
        sent.predicted_events.append(event)
        sentences_predicted_to_have_events.append(sent)



