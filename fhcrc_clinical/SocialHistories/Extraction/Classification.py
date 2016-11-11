import sklearn
import cPickle as Pickle
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import HashingVectorizer, CountVectorizer, TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.svm import SVC


def train_classifier(feature_dicts, labels):
    # Convert Data to vectors
    sent_vectors, labels_for_classifier, feature_map = vectorize_train_data(feature_dicts, labels)

    # Create Model
    classifier = SVC(kernel="linear", probability=True)
    classifier.fit(sent_vectors, labels_for_classifier)

    return classifier, feature_map


def vectorize_train_data(sentences, labels):
    # convert to vectors
    dict_vec = DictVectorizer(sparse=True)
    sentence_vectors = dict_vec.fit_transform(sentences)#.toarray()
    # map features to the appropriate index in the established SVM vector representation for each classifier
    feature_names = dict_vec.get_feature_names()
    feature_map = {}
    for index, feat in enumerate(feature_names):
        feature_map[feat] = index

    return sentence_vectors, np.array(labels), feature_map


def transform_svm_nums_to_probabilities(decision_func_results):
    probabilities = list()
    for result_array in decision_func_results:
        max_result = max(result_array)
        probability = 1 / (1 + np.math.exp(-max_result))
        probabilities.append(probability)
    return probabilities


def classify_many_instances(classifier, feature_map, features_per_instance):
    number_of_sentences = len(features_per_instance)
    number_of_features = len(feature_map)

    # Vectorize sentences and classify
    test_vectors = [vectorize_sentence(feats, feature_map) for feats in features_per_instance]
    test_array = np.reshape(test_vectors, (number_of_sentences, number_of_features))
    classifications = classifier.predict(test_array)
    #decision_func_results = classifier.decision_function(test_array)
    probabilities = classifier.predict_proba(test_array)#transform_svm_nums_to_probabilities(decision_func_results)

    return classifications, probabilities


def classify_instance(classifier, feature_map, features):
    number_of_sentences = 1
    number_of_features = len(feature_map)

    # Vectorize sentences and classify
    test_vectors = vectorize_sentence(features, feature_map)
    test_array = np.reshape(test_vectors, (number_of_sentences, number_of_features))
    classifications = classifier.predict(test_array)

    return classifications


def vectorize_sentence(feats, feature_map):
    vector = [0 for _ in range(len(feature_map))]
    grams = feats.keys()
    for gram in grams:
        if gram in feature_map:
            index = feature_map[gram]
            vector[index] = 1
    return vector


def load_classifier(classifier_file, feature_map_file):
    classifier = None
    feature_map = None

    try:
        classifier = sklearn.externals.joblib.load(classifier_file)
        feature_map = Pickle.load(open(feature_map_file, "rb"))
    except IOError:
        print("Error: can't find trained models. Run \"train_models.py\" and make sure model files are in the correct "
              "location with the correct name \n we looked in the following dir: \n\t" + classifier_file)

    return classifier, feature_map
