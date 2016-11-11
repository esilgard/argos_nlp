import re

from fhcrc_clinical.SocialHistories.Extraction.EventDetection.Processing import load_flor_patients
from fhcrc_clinical.SocialHistories.SystemUtilities import Globals


def get_feature_vectors(sents):
    feature_vecs = list()
    for sent in sents:
        vectors = dict()
        uni_feats, unigrams = get_unigrams(sent.text)
        vectors.update(uni_feats)
        vectors.update(get_bigrams(unigrams))
        # vectors.update(get_trigrams(unigrams))
        feature_vecs.append(vectors)
    return feature_vecs


def flor_get_feature_vectors():
    # Mapping flor labels to our labels
    mapping = {"past": Globals.FORMER, "user": Globals.USER, "non": Globals.NON, "current": Globals.CURRENT,
               "unknown": Globals.UNKNOWN}
    doc_data = load_flor_patients()

    feature_vecs = list()
    labels = list()

    for doc_id in doc_data:
        doc = doc_data[doc_id]
        for sent in doc:
            vector = dict()
            label = mapping[sent['TobaccoStatus']]  # whatever the tobacco status is for this entry
            uni_feats, input_list = get_unigrams(sent["Sentence"])
            vector.update(uni_feats)
            vector.update(get_bigrams(input_list))
            # vectors.update(get_trigrams(unigrams))
            feature_vecs.append(vector)
            labels.append(label)
    return feature_vecs, labels


def get_unigrams(sent):
    unigrams = re.sub('[,.!?:;()~]', '', sent.lower()).split()
    uni_feats = dict()
    for i in range(0, len(unigrams), 1):
        replacement = None
        # 1 or 2 numbers in a row (or more) is a NUM
        if re.match("[0-9]{1,3}(-[0-9]{1,3})*$", unigrams[i])is not None\
                or re.match("one|two|three|four|five|six|seven|eight|nine|ten", unigrams[i]) is not None \
                or re.match("[0-9]*\.[0-9]+", unigrams[i]) is not None:
            replacement = "NUM"
        # 1 or 2 numbers in a row directly attached to sequence of letters is an AMOUNT
        if re.match("[0-9]{1,2}(/[0-9])*[A-Za-z]+", unigrams[i]) is not None:
            replacement = "AMOUNT"
        # 4 numbers in a row (1998) or common date formats (12/12/95, 4/2016, 1-3-1988) are DATEs
        if re.match("[0-9]{4}", unigrams[i]) is not None \
                or re.match("[0-9]+-[0-9]+-[0-9]+$", unigrams[i]) is not None \
                or re.match("[0-9]+/[0-9]+/[0-9]+$", unigrams[i]) is not None \
                or re.match("[0-9]+/[0-9]+$", unigrams[i]) is not None \
                or re.match("[0-9]{2,4}(')*s", sent[i]) is not None:  # 1980's 80s 80's etc
            replacement = "DATE"
        if replacement is not None:
            unigrams[i] = replacement
        uni_feats[unigrams[i]] = True
    return uni_feats, unigrams


def get_bigrams(input_list):
    bigrams = zip(input_list, input_list[1:])
    bi_feats = dict()
    for bigram in bigrams:
        bi_feats[str(bigram[0]) + "_" + str(bigram[1])] = True
    return bi_feats


def get_trigrams(input_list):
    trigrams =zip(input_list, input_list[1:], input_list[2:])
    tri_feats = dict()
    for tri in trigrams:
        tri_feats[str(tri[0]) + "_" + str(tri[1]) + "_" + str(tri[2])] = True
    return tri_feats

