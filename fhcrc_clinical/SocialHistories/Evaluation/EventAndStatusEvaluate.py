from Evaluate import *
from fhcrc_clinical.KeywordSearch.KeywordGlobals import *
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import DATA_DIR
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import UNKNOWN


def evaluate_status_classification(patients):
    """ Evaluate sentence and document level status"""
    sentence_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}
    doc_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}
    # Find tp, fp, fn
    for patient in patients:
        for doc in patient.doc_list:
            # Evaluate each document
            evaluate_doc_status_classification(doc, doc_eval_data)

            # Evaluate each sentence
            for sent in doc.sent_list:
                evaluate_sentence_status_classification(sent, sentence_eval_data)

    # Precision and recall
    calculate_and_output_eval(sentence_eval_data, doc_eval_data, "statusclassf")

def evaluate_event_detection(patients):
    """ Evaluate sentence and document level substance status info detection """
    sentence_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}
    doc_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}

    # Find tp, fp, fn
    for patient in patients:
        for doc in patient.doc_list:
            # Evaluate each document
            evaluate_doc_event_detection(doc, doc_eval_data)

            # Evaluate each sentence
            for sent in doc.sent_list:
                evaluate_sentence_event_detection(sent, sentence_eval_data)

    # Precision and recall
    calculate_and_output_eval(sentence_eval_data, doc_eval_data, "eventdetect")


def calculate_and_output_eval(sentence_eval_data, doc_eval_data, eventDetect_or_statusClassf):
    for substance in SUBSTANCE_TYPES:
        # Calculate precision and recall
        sentence_eval_data[substance].calculate_precision_recall_f1()
        doc_eval_data[substance].calculate_precision_recall_f1()

        sentence_filename=""
        doc_filename=""
        if eventDetect_or_statusClassf == "eventdetect":
            # Output evaluation
            sentence_filename = os.path.join(DATA_DIR, "Evaluation","SentEventDetectionEval", substance)
            doc_filename = os.path.join(DATA_DIR, "Evaluation", "DocEventDetectionEval", substance)
        elif eventDetect_or_statusClassf == "statusclassf":
            # Output evaluation
            sentence_filename = os.path.join(DATA_DIR, "Evaluation", "SentStatusClassificationEval", substance)
            doc_filename = os.path.join(DATA_DIR, "Evaluation", "DocStatusClassificationEval", substance)

        sentence_eval_data[substance].output(sentence_filename)
        doc_eval_data[substance].output(doc_filename)


def evaluate_sentence_status_classification(sent, sentence_eval_data):
    gold_subs_status_dict = get_subs_status_dict(sent, "gold")
    predicted_subs_status_dict = get_subs_status_dict(sent, "predicted")

    compare_gold_and_predicted_status(gold_subs_status_dict, predicted_subs_status_dict, sentence_eval_data, sent.text)
    pass


def evaluate_sentence_event_detection(sent, sentence_eval_data):
    gold_substs = [g.substance_type for g in sent.gold_events]  # find_sent_gold_substs(sent, doc)
    predicted_substs = [p.substance_type for p in sent.predicted_events]

    compare_gold_and_predicted_substances(gold_substs, predicted_substs, sentence_eval_data, sent.text)


def get_subs_status_dict(data_obj, gold_or_predicted):
    subs_status_dict = dict()
    for subs in SUBSTANCE_TYPES:
        subs_status_dict[subs]=""

    if gold_or_predicted == "predicted":
        for event in data_obj.predicted_events:
            subs_status_dict[event.substance_type] = event.status
    elif gold_or_predicted == "gold":
        for event in data_obj.gold_events:
            subs_status_dict[event.substance_type] = event.status

    return subs_status_dict


def evaluate_doc_status_classification(doc, doc_eval_data):
    gold_subs_status_dict = get_subs_status_dict(doc, "gold")
    predicted_subs_status_dict = get_subs_status_dict(doc, "predicted")

    compare_gold_and_predicted_status(gold_subs_status_dict, predicted_subs_status_dict, doc_eval_data, doc.id)
    pass


def evaluate_doc_event_detection(doc, doc_eval_data):
    gold_substs = {event.substance_type for event in doc.gold_events
                   if (event.status and event.status != UNKNOWN)}
    predicted_substs = {event.substance_type for event in doc.predicted_events}

    compare_gold_and_predicted_substances(gold_substs, predicted_substs, doc_eval_data, doc.id)
    pass


def compare_gold_and_predicted_status(gold_subs_status_dict, predicted_subs_status_dict, eval_data_per_substance, text):
    """ Count tp,fp, fn for each subs status """
    # Find true positives, false positives
    for subs_type in predicted_subs_status_dict:
        if subs_type != "Secondhand":
            if gold_subs_status_dict[subs_type] == predicted_subs_status_dict[subs_type]:
                if predicted_subs_status_dict[subs_type] != "" and predicted_subs_status_dict[subs_type] != UNKNOWN:
                    eval_data_per_substance[subs_type].tp += 1
            else:
                eval_data_per_substance[subs_type].fp += 1
                eval_data_per_substance[subs_type].fp_values.append(text)
    # find false negatives
    for subs_type in gold_subs_status_dict:
        if subs_type != "Secondhand":
            if gold_subs_status_dict[subs_type] != predicted_subs_status_dict[subs_type]:
                if predicted_subs_status_dict[subs_type] != "" and predicted_subs_status_dict[subs_type] != UNKNOWN:
                    eval_data_per_substance[subs_type].fn += 1
                    eval_data_per_substance[subs_type].fn_values.append(text)


def compare_gold_and_predicted_substances(gold_substs, predicted_substs, eval_data_per_substance, text):
    """ Record matches and mismatches for each substance """
    # Find true pos, false pos
    for classification in predicted_substs:
        if classification in gold_substs:
            eval_data_per_substance[classification].tp += 1
        else:
            eval_data_per_substance[classification].fp += 1
            eval_data_per_substance[classification].fp_values.append(text)
    # Find false neg
    for classification in gold_substs:
        if classification not in predicted_substs:
            eval_data_per_substance[classification].fn += 1
            eval_data_per_substance[classification].fn_values.append(text)


def find_sent_gold_substs(sent, doc):
    """@type doc: Document"""
    gold_substs = set()
    for substance in doc.highlighted_spans:
        for gold_span in doc.highlighted_spans[substance]:
            overlap = has_overlap(gold_span.start, gold_span.stop, sent.span_in_doc_start, sent.span_in_doc_end)
            if overlap:
                gold_substs.add(substance)
    return gold_substs
