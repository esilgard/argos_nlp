import re

def get_feature_vectors(sents):
    feature_vecs = list()
    for sent in sents:
        vectors = dict()
        uni_feats, unigrams = get_unigrams(sent)
        vectors.update(uni_feats)
        # vectors.update(get_bigrams(unigrams))
        # vectors.update(get_trigrams(unigrams))
        feature_vecs.append(vectors)
    return feature_vecs


def get_unigrams(sent):
    unigrams = re.sub('[,.!?:;()~]', '', sent.text.lower()).split()
    uni_feats = dict()
    for i in range(0,len(unigrams),1):
        replacement=None
        # 1 or 2 numbers in a row (or more) is a NUM
        if re.match("[0-9]{1,2}", unigrams[i])!=None:
            replacement="NUM"
        # 1 or 2 numbers in a row directly attached to sequence of letters is an AMOUNT
        if re.match("[0-9]{1,2}[A-Za-z]+", unigrams[i]) !=None:
            replacement="AMOUNT"
        # 4 numbers in a row (1998) or common date formats (12/12/95, 1-3-1988) are DATEs
        if re.match("[0-9]{4}", unigrams[i]) is not None \
                or re.match("[0-9]+-[0-9]+-[0-9]+", unigrams[i]) is not None \
                or re.match("[0-9]+/[0-9]+/[0-9]+", unigrams[i]) is not None:
            replacement="DATE"
        if replacement is not None:
            unigrams[i]=replacement
        uni_feats[unigrams[i]] = True
    #debug
    #print unigrams
    #tmp=0
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
