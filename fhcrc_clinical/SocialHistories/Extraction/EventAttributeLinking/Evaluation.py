from DataModeling.DataModels import *
from Extraction.GeneralEvaluation import *
from SystemUtilities.Configuration import *
from Preprocessing.generate_notes import load_caisis_silver_annotations


def evaluate(patients):
    """ Evaluate sentence and document level substance status info detection """
    fn_docs = {subst: [] for subst in SUBSTANCE_TYPES}  # {event type : [doc_id]}
    fp_docs = {subst: [] for subst in SUBSTANCE_TYPES}  # {event type : [doc_id]}
    tp = 0
    fn = 0
    fp = 0

    # Find tp, fp, fn
    for patient in patients:
        for doc in patient.doc_list:
            tp, fp, fn = evaluate_doc(doc, fn, fp, tp, fp_docs, fn_docs)

    # Precision and recall
    precision_doc, recall_doc, f1_doc = calculate_precision_recall_f1(tp, fp, fn)

    # Output evaluation
    # TODO -- output_evaluation(precision_doc, recall_doc, f1_doc, fn_docs, fp_docs)


def evaluate_doc(doc, fn, fp, tp, fp_docs, fn_docs):
    """@type doc: Document"""
    gold_attribs = get_attributes(doc.gold_events)
    predicted_substs = get_attributes(doc.predicted_events)

    # TODO tp, fp, fn = compare_gold_and_predicted(gold_attribs, predicted_substs, fn_docs, fp_docs, doc.id, tp, fp, fn)
    return tp, fp, fn


def get_attributes(doc_events):
    attributes = {subst: [] for subst in SUBSTANCE_TYPES} # {substance: [Attrribute]}

    for event in doc_events:
        for attribute in event.attributes:
            for span in attribute.all_span_values:
                attrib_obj = Attribute(attribute, )

    return attributes
