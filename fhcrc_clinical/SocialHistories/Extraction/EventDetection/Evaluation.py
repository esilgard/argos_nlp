from DataModeling.DataModels import *
from Extraction.GeneralEvaluation import *
from SystemUtilities.Configuration import *
from Processing import *


def evaluate(patients):
    """ Evaluate sentence and document level substance status info detection """
    fn_sents = {subst: [] for subst in SUBSTANCE_TYPES}   # {event type : [sentences]}
    fp_sents = {subst: [] for subst in SUBSTANCE_TYPES}   # {event type : [sentences]}
    tp_sent = 0
    fn_sent = 0
    fp_sent = 0

    fn_docs = {subst: [] for subst in SUBSTANCE_TYPES}  # {event type : [doc_id]}
    fp_docs = {subst: [] for subst in SUBSTANCE_TYPES}  # {event type : [doc_id]}
    tp_doc = 0
    fn_doc = 0
    fp_doc = 0

    # Find tp, fp, fn
    for patient in patients:
        for doc in patient.doc_list:
            # Evaluate each document
            tp_doc, fp_doc, fn_doc = evaluate_doc(doc, fn_docs, fp_docs, tp_doc, fp_doc, fn_doc)

            # Evaluate each sentence
            for sent in doc.sent_list:
                tp_sent, fp_sent, fn_sent = evaluate_sentence(sent, fn_sents, fp_sents, tp_sent, fp_sent, fn_sent)

    # Precision and recall
    precision_sent, recall_sent, f1_sent = calculate_precision_recall_f1(tp_sent, fp_sent, fn_sent)
    precision_doc, recall_doc, f1_doc = calculate_precision_recall_f1(tp_doc, fp_doc, fn_doc)

    # Output evaluation
    output_evaluation(precision_sent, recall_sent, f1_sent, fp_sents, fn_sents,
                      precision_doc, recall_doc, f1_doc, fn_docs, fp_docs)


def evaluate_sentence(sent, fn_sents, fp_sents, tp, fp, fn):
    """@type sent: Sentence"""
    gold_substs = [g.substance_type for g in sent.gold_events]  # find_sent_gold_substs(sent, doc)
    predicted_substs = [p.substance_type for p in sent.predicted_events]

    tp, fp, fn = compare_gold_and_predicted(gold_substs, predicted_substs, fn_sents, fp_sents, sent.text, tp, fp, fn)
    return tp, fp, fn


def evaluate_doc(doc, fn_docs, fp_docs, tp_doc, fp_doc, fn_doc):
    """@type doc: Document"""
    gold_substs = {event.substance_type for event in doc.gold_events if (event.substance_type and event.substance_type != UNKNOWN)}
    predicted_substs = {event.substance_type for event in doc.predicted_events}

    tp, fp, fn = compare_gold_and_predicted(gold_substs, predicted_substs, fn_docs, fp_docs, doc.id,
                                            tp_doc, fp_doc, fn_doc)
    return tp, fp, fn


def compare_gold_and_predicted(gold_substs, predicted_substs, fn_sents, fp_sents, text, tp, fp, fn):
    # Find true pos, false pos
    for classf in predicted_substs:
        if classf in gold_substs:
            tp += 1
        else:
            fp += 1
            fp_sents[classf].append(text)
    # Find false neg
    for classf in gold_substs:
        if classf not in predicted_substs:
            fn += 1
            fn_sents[classf].append(text)
    return tp, fp, fn


def find_sent_gold_substs(sent, doc):
    """@type doc: Document"""
    gold_substs = set()
    for substance in doc.highlighted_spans:
        for gold_span in doc.highlighted_spans[substance]:
            overlap = check_sent_overlap(gold_span.start, gold_span.stop, sent.span_in_doc_start, sent.span_in_doc_end)
            if overlap:
                gold_substs.add(substance)
    return gold_substs


def output_evaluation(precision_sent, recall_sent, f1_sent, fp_sents, fn_sents,
                      precision_doc, recall_doc, f1_doc, fn_docs, fp_docs):
    out_file = open(CLASSF_EVAL_FILENAME, "w")

    # Precision/recall
    out_file.write("\nClassifier Evaluation " + "\n---------------------\n")
    out_file.write("Sentence-Level: " + "\n")
    out_file.write("Precision: " + str(precision_sent) + "\n")
    out_file.write("Recall: " + str(recall_sent) + "\n\n")
    out_file.write("F1: " + str(f1_sent) + "\n\n")

    out_file.write("Document-Level: " + "\n")
    out_file.write("Precision: " + str(precision_doc) + "\n")
    out_file.write("Recall: " + str(recall_doc) + "\n\n")
    out_file.write("F1: " + str(f1_doc) + "\n\n")

    # Output misclassified elements for debugging/evaluation
    out_file.write("<< FP Sentences >>\n")
    output_misclassified_elements(fp_sents, out_file)

    out_file.write("<< FN Sentences >>\n")
    output_misclassified_elements(fn_sents, out_file)

    out_file.write("<< FP Documents >>\n")
    output_misclassified_elements(fp_docs, out_file)

    out_file.write("<< FN Documents >>\n")
    output_misclassified_elements(fn_docs, out_file)


def output_misclassified_elements(elements, out_file):
    for event_type in elements:
        out_file.write(event_type + "\n")
        for sent in elements[event_type]:
            out_file.write(sent + "\n")
    out_file.write("\n")
