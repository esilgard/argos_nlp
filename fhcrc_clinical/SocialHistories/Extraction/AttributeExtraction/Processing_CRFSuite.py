import nltk
import re

from fhcrc_clinical.SocialHistories.Extraction.AttributeExtraction.Patterns import *
from fhcrc_clinical.SocialHistories.SystemUtilities.Parameter_Configuration import SENTENCE_TOK_PATTERN


def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    features = [
        'bias',
        'word.lower=' + word.lower(),
        'numdashes=' + str(num_dashes(word)),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.matchesTIMEEXPR=%s' % matches_TIMEEXPR(word),
        'word.matchesNUM=%s' % matches_NUM(word),
        'word.matchesYEARNUM=%s' % matches_YEARNUM(word),
        'postag=' + postag,
        'postag[:2]=' + postag[:2],
    ]
    if i > 0:
        word1 = sent[i - 1][0]
        postag1 = sent[i - 1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:numdashes=' + str(num_dashes(word1)),
            '-1:word[-3:]=' + word1[-3:],
            '-1:word[-2:]=' + word1[-2:],
            '-1:word.matchesTIMEEXPR=%s' % matches_TIMEEXPR(word1),
            '-1:word.matchesNUM=%s' % matches_NUM(word1),
            '-1:word.matchesYEARNUM=%s' % matches_YEARNUM(word1),
            '-1:postag=' + postag1,
            '-1:postag[:2]=' + postag1[:2],

        ])
    else:
        features.append('BOS')

    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        postag1 = sent[i + 1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:numdashes=' + str(num_dashes(word1)),
            '+1:word[-3:]=' + word1[-3:],
            '+1:word[-2:]=' + word1[-2:],
            '+1:word.matchesTIMEEXPR=%s' % matches_TIMEEXPR(word1),
            '+1:word.matchesNUM=%s' % matches_NUM(word1),
            '+1:word.matchesYEARNUM=%s' % matches_YEARNUM(word1),
            '+1:postag=' + postag1,
            '+1:postag[:2]=' + postag1[:2],
        ])
    else:
        features.append('EOS')
    #window of +/- 2
    if i < len(sent)-2:
        word2 = sent[i+2][0]
        postag2 = sent[i+2][1]
        features.extend([
            '+2:word[-3:]=' + word2[-3:],
            '+2:word[-2:]=' + word2[-2:],
            '+2:word.matchesTIMEEXPR=%s' % matches_TIMEEXPR(word2),
            '+2:word.matchesNUM=%s' % matches_NUM(word2),
            '+2:word.matchesYEARNUM=%s' % matches_YEARNUM(word2),
            '+2:word.lower=' + word2.lower(),
            '+2:postag=' + postag2,
        ])
    else:
        features.append('EOS')
    if i > 1:
        word2 = sent[i-2][0]
        postag2 = sent[i-2][1]
        features.extend([
            '-2:word[-3:]=' + word2[-3:],
            '-2:word[-2:]=' + word2[-2:],
            '-2:word.matchesNUM=%s' % matches_NUM(word2),
            '-2:word.matchesTIMEEXPR=%s' % matches_TIMEEXPR(word2),
            '-2:word.matchesYEARNUM=%s' % matches_YEARNUM(word2),
            '-2:word.lower=' + word2.lower(),
            '-2:postag=' + postag2,
        ])
    # window of +/- 3
    if i < len(sent)-3:
        word3 = sent[i+3][0]
        postag3 = sent[i+3][1]
        features.extend([
            '+3:word.lower=' + word3.lower(),
            '+3:postag=' + postag3,
        ])
    else:
        features.append('EOS')
    if i > 2:
        word3 = sent[i-3][0]
        postag3 = sent[i-3][1]
        features.extend([
            '-3:word.lower=' + word3.lower(),
            '-3:postag=' + postag3,
        ])
    #print features
    return features


def tokenize_sentences(sentences, attrib_type=None, training=False):
    tokenized_sentences = list()
    tokenized_labels = list()
    for sent_obj in sentences:
        sentence_toks = list()
        label_toks = list()
        tokenization_pattern = SENTENCE_TOK_PATTERN
        if training:
            _tokenize_and_span_match_training(sent_obj,tokenization_pattern, sentence_toks, label_toks,attrib_type)
            tokenized_sentences.append(sentence_toks)
            tokenized_labels.append(label_toks)
        else:
            for match in nltk.re.finditer(tokenization_pattern, sent_obj.text):
                word = match.group(0).rstrip(".?;:")
                if word != "":
                    sentence_toks.append(word)
            tokenized_sentences.append(sentence_toks)
    return tokenized_sentences, tokenized_labels


# def standardize_tokens_list(sent_toks_list):
#     new_sent_toks_list = []
#     for sent in sent_toks_list:
#         s =standardize_tokens(sent)
#         new_sent_toks_list.append(s)
#     return new_sent_toks_list





def _tokenize_and_span_match_training(sent_obj, tokenization_pattern, sentence_toks, label_toks, attrib_type):
    if len(sent_obj.gold_events) > 0:  # if the sentence has an event
        sentence = sent_obj.text
        gold_event_set = sent_obj.gold_events
        sent_offset = sent_obj.span_in_doc_start
        for match in nltk.re.finditer(tokenization_pattern, sentence):
            start = match.start()
            end = match.end()
            pointer = sent_offset + start
            word = match.group(0)
            sentence_toks.append(word)
            answer = "0"
            debug_str = ""
            appended = False
            for entity in gold_event_set:
                if answer != "0":
                    break
                attr_dict = entity.attributes
                for attr in attr_dict:
                    for span in attr_dict[attr].all_value_spans:
                        attr_start = int(span.start)
                        attr_end = int(span.stop)
                        if attr_dict[attr].type == attrib_type and \
                                                attr_start <= pointer < attr_end:  # < attr_end
                            answer = attrib_type
                            label_toks.append(answer)
                            appended = True
                            break
            if not appended:
                label_toks.append(answer)


def get_sentences_with_subsinfo_from_patients(patients):
    sentences = list()
    for patient in patients:
        for document in patient.doc_list:
            for sent_obj in document.sent_list:
                if (len(sent_obj.gold_events)) > 0:  # if the sentence has an event
                    sentences.append(sent_obj)
    return sentences


def get_sentences_from_patients(patients):
    sentences = list()
    for patient in patients:
        for document in patient.doc_list:
            for sent_obj in document.sent_list:
                sentences.append(sent_obj)
    return sentences


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2labels(sent):
    return [label for token, postag, label in sent]


def sent2tokens(sent):
    return [token for token in sent]


def sent2tokensWLabels(sent):
    return [token for token, postag, label in sent]


def is_number(s):
    try:
        float(s)
    except ValueError:
        if s == "num" or s =="NUM" or \
                        s == "NUMRANGE" or s == "numrange" or \
                        s == "YEARNUM" or s == "yearnum" or \
                        s == "AMOUNT" or s == "amount":
            return s

        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def remove_vowels(line):
    return re.sub('[aeiou]', '', line)


def num_dashes(word):
    divs = word.split("-")
    return len(divs)-1

def refers_to_packs(word):
    pack_words = {"pk", "pack", "packs"}
    if word in pack_words:
        return True
    return False

def has_plus(word):
    divs = word.split("+")
    if len(divs)>1:
        return True
    else:
        return False