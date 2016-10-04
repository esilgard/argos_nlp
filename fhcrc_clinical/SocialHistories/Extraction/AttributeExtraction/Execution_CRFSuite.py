import nltk
import pycrfsuite

from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Attribute
from fhcrc_clinical.SocialHistories.Extraction.AttributeExtraction.Processing_CRFSuite import sent2features
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import ATTRIB_EXTRACTION_DIR_HOME, entity_types


def extract(patients, model_path=ATTRIB_EXTRACTION_DIR_HOME):
    # Extract all sentences with subs info + the sentence after
    all_sentences = get_sentences_with_info_plus_sentence_after(patients)

    for type in entity_types: # {Amount, Duration, QuiteDate, TimeAgo, QuitAge, SecondhandAmount}
        model_name = model_path + "Models/" + "model-" + type + ".ser.gzwl"
        test(all_sentences, model_name, type)
    print("Finished CRF classification")


def test(test_sents, model_name, type):
    print "testing NER tagger ..."
    tagger = pycrfsuite.Tagger()
    tagger.open(model_name)
    tagged_sents = list()
    for sent in test_sents:
        # Tag for POS
        tagged_sent = nltk.pos_tag(sent.text.split())
        tagged_sents.append(tagged_sent)
        # Recover spans
        tokenized_text, spans = recover_spans(sent.text)
        # Predict type sequence
        predictions = tagger.tag(sent2features(tagged_sent))
        classified_text = zip(tokenized_text,predictions)
        # Expand tuple to have span as well
        len_diff = 0#len(spans) - len(classified_text)  # Headers were stripped, so if this occured in the previous step, we have t account for the offset
        final_class_and_span = list()
        for idx, tup in enumerate(classified_text):
            combined = (
            classified_text[idx][0], classified_text[idx][1], spans[idx + len_diff][0], spans[idx + len_diff][1])
            final_class_and_span.append(combined)
        #print(classified_text)
        # Set prediction in sentence object
        sent.sentence_attribs.extend(get_attributes(final_class_and_span))



def recover_spans(text):
    tokenized_text = list()
    spans = list()
    for match in nltk.re.finditer("\S+", text):
        start = match.start()
        end = match.end()
        word = match.group(0)
        tokenized_text.append(word)
        spans.append((start, end))
    return tokenized_text, spans


def get_sentences_with_info_plus_sentence_after(patients):
    all_sents = list()
    for patient in patients:
        for document in patient.doc_list:
            grab_next = False
            for sentence in document.sent_list:
                if len(sentence.predicted_events) > 0 or grab_next:
                    if grab_next:
                        grab_next = False
                    if len(sentence.predicted_events) > 0:
                        grab_next = True
                    all_sents.append(sentence)
    return all_sents


def get_attributes(crf_classification_tuple_list):
    attribs = list()
    i = 0
    while i < len(crf_classification_tuple_list)-1:
        crf_classification_tuple = crf_classification_tuple_list[i]
        classL = crf_classification_tuple[1]
        start = crf_classification_tuple[2]
        if classL != "0": # beginning of a labeled span
            full_begin_span = start
            full_end_span = start
            full_text = ""
            while i < len(crf_classification_tuple_list)-1 and classL == crf_classification_tuple_list[i][1]:
                crf_classification_tuple = crf_classification_tuple_list[i]
                full_text += crf_classification_tuple[0] + " "
                full_end_span = crf_classification_tuple[3]
                i += 1
            attrib = Attribute(classL, full_begin_span, full_end_span, full_text)
            attribs.append(attrib)
        i += 1
    return attribs