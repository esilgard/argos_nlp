# coding=utf-8
from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite

from fhcrc_clinical.SocialHistories.Extraction.AttributeExtraction.Execution_CRFSuite import test
from fhcrc_clinical.SocialHistories.Extraction.AttributeExtraction.Processing_CRFSuite import sent2features, \
    get_sentences_with_subsinfo_from_patients, tokenize_sentences
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import ATTRIB_EXTRACTION_DIR_HOME
from fhcrc_clinical.SocialHistories.SystemUtilities import Debug_Methods
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import entity_types


def train(patients, model_path=ATTRIB_EXTRACTION_DIR_HOME):
    print "training Subs_Amount tagger ..."
    sentence_objs = get_sentences_with_subsinfo_from_patients(patients)
    for type in entity_types:
        model_name = model_path + r"Models/" + "model-" + type + ".ser.gz"
        training_sents, training_labels = load_train_data(sentence_objs,type)
        # DEBUG
        Debug_Methods.write_training_data_as_file(training_sents, training_labels, sentence_objs)
        # END DEBUG
        x_train, y_train = get_features_and_labels(training_sents, training_labels)
        train_data(x_train, y_train, model_name+"wl")
        print("CRF model written to: " + model_name+"wl")


def load_train_data(sentences, attrib_type):
    return tokenize_sentences(sentences, attrib_type, training=True)


def train_data(x_train, y_train, model_name):
    trainer = pycrfsuite.Trainer(verbose=True)
    for xseq, yseq in zip(x_train, y_train):
        trainer.append(xseq, yseq)

    trainer.set_params({
        'c1': .1,#1.0,  # coefficient for L1 penalty
        'c2': .1, #1e-3,  # coefficient for L2 penalty
        'max_iterations': 100,  # stop earlier

        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
    trainer.train(model_name) # produces model file with this name
    pass


def get_features_and_labels(sents, labels):
    # Tag for POS
    tagged_sents = list()
    for sent in sents:
        tagged_sent = nltk.pos_tag(sent)
        tagged_sents.append(tagged_sent)

    x = [sent2features(s) for s in tagged_sents]
    y = labels #[sent2labels(s) for s in labels]
    return x, y