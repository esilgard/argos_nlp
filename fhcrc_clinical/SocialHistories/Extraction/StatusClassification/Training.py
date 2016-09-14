import cPickle as Pickle
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
import numpy as np

from fhcrc_clinical.SocialHistories.Extraction.EventDetection.Processing import flor_sentence_features_and_labels, load_flor_patients
from fhcrc_clinical.SocialHistories.SystemUtilities import Globals
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import MODEL_DIR
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import STATUS_CLASSF_FEATMAP_SUFFIX, STATUS_CLASSF_MODEL_SUFFIX


def train_status_classifier(patients):
    sentences = get_sentences_from_patients(patients)

    # Load Florian data
    flor_tbc_feats, flor_tbc_labels = flor_get_tob_features()

    # Create Feature-Label pairs for each Subs Abuse type
    alc_feats, alc_labels = get_features(sentences, Globals.ALCOHOL)
    tbc_feats, tbc_labels = get_features(sentences, Globals.TOBACCO)
    #scd_hnd_feats, scd_hnd_labels = get_features(sentences, Globals.SECONDHAND)

    # Join flor's tobacco features and labels to regular tobacco features and labels
    tbc_feats.extend(flor_tbc_feats)
    tbc_labels.extend(flor_tbc_labels)

    # Create Model
    alc_classifier, alc_feature_map = train_model(alc_feats, alc_labels)
    tob_classifier, tob_feature_map = train_model(tbc_feats, tbc_labels)
    #scd_hnd_classifier, scd_hnd_feature_map = train_model(scd_hnd_feats, scd_hnd_labels)

    # Set output directory pointers for model files
    classf_alc_file = MODEL_DIR + Globals.ALCOHOL + STATUS_CLASSF_MODEL_SUFFIX
    classf_tob_file = MODEL_DIR + Globals.TOBACCO + STATUS_CLASSF_MODEL_SUFFIX
    classf_scndhnd_file = MODEL_DIR + Globals.SECONDHAND + STATUS_CLASSF_MODEL_SUFFIX
    featmap_alc_file = MODEL_DIR + Globals.ALCOHOL + STATUS_CLASSF_FEATMAP_SUFFIX
    featmap_tob_file = MODEL_DIR + Globals.TOBACCO + STATUS_CLASSF_FEATMAP_SUFFIX
    featmap_scndhnd_file = MODEL_DIR + Globals.SECONDHAND + STATUS_CLASSF_FEATMAP_SUFFIX


    # write models files
    joblib.dump(alc_classifier, classf_alc_file)
    Pickle.dump(alc_feature_map, open(featmap_alc_file, "wb"))
    joblib.dump(tob_classifier, classf_tob_file)
    Pickle.dump(tob_feature_map, open(featmap_tob_file, "wb"))
    # joblib.dump(scd_hnd_classifier, classf_scndhnd_file)
    # Pickle.dump(scd_hnd_feature_map, open(featmap_scndhnd_file, "wb"))
    pass

def get_sentences_from_patients(patients):
    sentences = list()
    for patient in patients:
        for document in patient.doc_list:
            for sent_obj in document.sent_list:
                if (len(sent_obj.gold_events)) > 0: # if the sentence has an event
                    sentences.append(sent_obj)
    return sentences

def flor_get_tob_features():
    # Mapping flor labels to our labels
    mapping = {"past":Globals.FORMER, "user":Globals.USER, "non":Globals.NON, "current":Globals.CURRENT, "unknown":Globals.UNKNOWN}
    doc_data = load_flor_patients()

    feature_vecs = list()
    labels = list()

    for doc_id in doc_data:
        doc = doc_data[doc_id]
        for sent in doc:
            vector = dict()
            label = mapping[sent['TobaccoStatus']] # whatever the tobacco status is for this entry
            input_list = sent["Sentence"].lower().rstrip(",.!?:;").split()
            some_bigrams = list(get_bigrams(input_list))

            for pair in some_bigrams:
                vector[pair[0] + "_" + pair[1]] = True
            for x in input_list:
                vector[x] = True

            labels.append(label)
            feature_vecs.append(vector)
    return feature_vecs, labels


def get_features(sents, subs_type):
    feature_vecs = list()
    labels = list()
    for sent in sents:
        vector = dict()
        label, evidence =sent.get_status_label_and_evidence(subs_type)
        input_list = sent.text.lower().rstrip(",.!?:;").split()
        some_bigrams = list(get_bigrams(input_list))

        for pair in some_bigrams:
            vector[pair[0] + "_" + pair[1]] = True
        for x in input_list:
            vector[x]=True

        labels.append(label)
        feature_vecs.append(vector)
    return feature_vecs, labels

def get_bigrams(input_list):
    return zip(input_list, input_list[1:])


def vectorize_data(sentences, labels):
    # convert to vectors
    dict_vec = DictVectorizer()
    sentence_vectors = dict_vec.fit_transform(sentences).toarray()

    # map features to the appropriate index in the established SVM vector representation for each classifier
    feature_names = dict_vec.get_feature_names()
    feature_map = {}
    for index, feat in enumerate(feature_names):
        feature_map[feat] = index

    return sentence_vectors, np.array(labels), feature_map


def train_model(proc_sents, labels):
        # Convert Data to vectors
        sent_vectors, labels_for_classifier, feature_map = vectorize_data(proc_sents, labels)

        # Create Model
        classifier = LinearSVC()
        classifier.fit(sent_vectors, labels_for_classifier)

        return classifier, feature_map
