from Evaluate import *
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Span
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import *
from fhcrc_clinical.SocialHistories.Extraction.EventDetection.Processing import has_overlap
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *


def evaluate_attributes(patients):
    """Evaluate value, the span of the value, and the spans of all highlighted regions for each attribute"""
    for attribute_type in ALL_ATTRIBS:
        value_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}
        value_span_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}
        all_span_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}
        all_span_overlap_eval_data = {subst: EvaluationData() for subst in SUBSTANCE_TYPES}

        # Find performance of attribute in each document
        for patient in patients:
            for doc in patient.doc_list:
                evaluate_doc_attribute(attribute_type, doc, value_eval_data, value_span_eval_data,
                                       all_span_eval_data, all_span_overlap_eval_data)

        # Output total performance
        evaluate_total_performance(attribute_type, value_eval_data, value_span_eval_data, all_span_eval_data,
                                   all_span_overlap_eval_data, attribute_type)


def evaluate_doc_attribute(attribute_type, doc, value_eval_data, value_span_eval_data, all_span_eval_data,
                           all_span_overlap_eval_data):
    """ For a specific attribute, find the correctness of selected value of attribute """
    gold_values, gold_value_spans, gold_all_spans = get_gold_field_data(attribute_type, doc)
    pred_values, pred_value_spans, pred_all_spans = get_predicted_field_data(attribute_type, doc)

    collect_doc_value_info(value_eval_data, gold_values, pred_values, doc)
    collect_doc_value_span_info(value_span_eval_data, gold_value_spans, pred_value_spans, doc)
    collect_doc_all_spans_info(all_span_eval_data, gold_all_spans, pred_all_spans, doc)
    collect_doc_all_spans_overlap_info(all_span_overlap_eval_data, gold_all_spans, pred_all_spans, doc)


def get_gold_field_data(attribute_type, doc):
    """ For a field, find the gold field value, the span of the value, and the spans of all highlighted regions """
    value = {subst: None for subst in SUBSTANCE_TYPES}       # {subst: value}
    value_span = {subst: None for subst in SUBSTANCE_TYPES}  # {subst: span}
    all_spans = {subst: [] for subst in SUBSTANCE_TYPES}     # {subst: [all_spans]}

    for event in doc.gold_events:
        event_attribute_data(event, attribute_type, value, value_span, all_spans)

    return value, value_span, all_spans


def get_predicted_field_data(attribute_type, doc):
    """ For a field, find the gold field value, the span of the value, and the spans of all highlighted regions """
    value = {subst: None for subst in SUBSTANCE_TYPES}       # {subst: value}
    value_span = {subst: None for subst in SUBSTANCE_TYPES}  # {subst: span}
    all_spans = {subst: [] for subst in SUBSTANCE_TYPES}     # {subst: [all_spans]}

    for event in doc.predicted_events:
        event_attribute_data(event, attribute_type, value, value_span, all_spans)

    return value, value_span, all_spans


def event_attribute_data(event, attribute_type, value, value_span, all_spans):
    if attribute_type in event.attributes:
        substance = event.substance_type
        attrib = event.attributes[attribute_type]

        value[substance] = attrib.text
        # value_span[substance] = Span(attrib.span_start, attrib.span_end)
        all_spans[substance] = attrib.all_value_spans


def collect_doc_value_info(value_eval_data, gold_values, pred_values, doc):
    """ Evaluate the selected value for field info """
    # Find performance for each substance
    for substance in value_eval_data:
        # Find TP, FN, FP
        find_value_eval_data(value_eval_data, substance, gold_values, pred_values, doc)


def find_value_eval_data(value_eval_data, substance, gold_values, pred_values, doc):
    # Find true pos, false pos
    if pred_values[substance]:
        if pred_values[substance] == gold_values[substance]:
            value_eval_data[substance].tp += 1
        else:
            value_eval_data[substance].fp += 1
            value_eval_data[substance].fp_values.append(doc.id + " " + pred_values[substance])
    # Find false neg
    if gold_values[substance]:
        if gold_values[substance] != pred_values[substance]:
            value_eval_data[substance].fn += 1
            value_eval_data[substance].fn_values.append(doc.id + " " + gold_values[substance])


def collect_doc_value_span_info(value_span_eval_data, gold_value_spans, pred_value_spans, doc):
    """ Evaluate the selected value for field info, using its text span """
    '''
    To do this you could copy find_all_span_eval_data, but for the predicted event instead of grabbing
    all_value_spans, you can just look at span_start and span_end, which represent the span for the chosen value

    for substance in value_span_eval_data:
        # Find TP, FN, FP
        find_value_span_eval_data(value_span_eval_data, substance, gold_value_spans, pred_value_spans)
    '''
    pass


def collect_doc_all_spans_info(all_span_eval_data, gold_all_spans, pred_all_spans, doc):
    """ Evaluate the detection of all instances of field info, using exact matches of text spans """
    # Find performance for each substance
    for substance in all_span_eval_data:
        # Find TP, FN, FP
        find_all_span_eval_data(all_span_eval_data, substance, gold_all_spans, pred_all_spans, doc)


def find_all_span_eval_data(all_span_eval_data, substance, gold_all_spans, pred_all_spans, doc):
    # Find true pos, false pos
    for pred_span in pred_all_spans[substance]:
        match_found = False

        # Check each predicted span for an equivalent in the gold
        for gold_span in gold_all_spans[substance]:
            if pred_span.start == gold_span.start and pred_span.stop == gold_span.stop:
                all_span_eval_data[substance].tp += 1
                match_found = True
                break

        # If none found, it's an FP
        if not match_found:
            all_span_eval_data[substance].fp += 1
            all_span_eval_data[substance].fp_values.append(doc.id + " " + doc.text[pred_span.start:pred_span.stop])
    # Find false neg
    for gold_span in gold_all_spans[substance]:
        match_found = False

        # Check each gold span for an equivalent in the predicted
        for pred_span in pred_all_spans[substance]:
            if pred_span.start == gold_span.start and pred_span.stop == gold_span.stop:
                match_found = True
                break

        # If none found, it's an FN
        if not match_found:
            all_span_eval_data[substance].fn += 1
            all_span_eval_data[substance].fn_values.append(doc.id + " " + doc.text[gold_span.start:gold_span.stop])


def collect_doc_all_spans_overlap_info(all_span_overlap_eval_data, gold_all_spans, pred_all_spans, doc):
    """ Evaluate the detection of all instances of field info, using matches based on overlap of text spans"""
    # Find performance for each substance
    for substance in all_span_overlap_eval_data:
        # Find TP, FN, FP
        find_all_span_overlap_eval_data(all_span_overlap_eval_data, substance, gold_all_spans, pred_all_spans, doc)


def find_all_span_overlap_eval_data(all_span_eval_data, substance, gold_all_spans, pred_all_spans, doc):
    # Find true pos, false pos
    for pred_span in pred_all_spans[substance]:
        match_found = False

        # Check each predicted span for an equivalent in the gold
        for gold_span in gold_all_spans[substance]:
            if has_overlap(pred_span.start, pred_span.stop, gold_span.start, gold_span.stop):
                all_span_eval_data[substance].tp += 1
                match_found = True
                break

        # If none found, it's an FP
        if not match_found:
            all_span_eval_data[substance].fp += 1
            all_span_eval_data[substance].fp_values.append(doc.id + " " + doc.text[pred_span.start:pred_span.stop])
    # Find false neg
    for gold_span in gold_all_spans[substance]:
        match_found = False

        # Check each gold span for an equivalent in the predicted
        for pred_span in pred_all_spans[substance]:
            if has_overlap(pred_span.start, pred_span.stop, gold_span.start, gold_span.stop):
                match_found = True
                break

        # If none found, it's an FN
        if not match_found:
            all_span_eval_data[substance].fn += 1
            all_span_eval_data[substance].fn_values.append(doc.id + " " + doc.text[gold_span.start:gold_span.stop])


def find_total_field_performance(eval_data_per_substance, attribute, output_file):
    total_eval_data = EvaluationData()

    # find tp, fp, fn
    for substance in eval_data_per_substance:
        subst_eval_data = eval_data_per_substance[substance]

        total_eval_data.tp += subst_eval_data.tp
        total_eval_data.fp += subst_eval_data.fp
        total_eval_data.fn += subst_eval_data.fn
        total_eval_data.fp_values.extend(subst_eval_data.fp_values)
        total_eval_data.fn_values.extend(subst_eval_data.fn_values)

    # find and output precision, recall
    total_eval_data.calculate_precision_recall_f1()
    total_eval_data.output(output_file + "_" + attribute + "_total")


def evaluate_total_performance(attribute_type, value_eval_data, value_span_eval_data, all_span_eval_data,
                               all_span_overlap_eval_data, attribute):
    for substance in SUBSTANCE_TYPES:
        # Precision, recall
        value_eval_data[substance].calculate_precision_recall_f1()
        # value_span_eval_data[substance].calculate_precision_recall_f1()
        all_span_eval_data[substance].calculate_precision_recall_f1()
        all_span_overlap_eval_data[substance].calculate_precision_recall_f1()

        # Output eval
        value_eval_data[substance].output(ATTRIB_VALUE_EVAL_FILENAME + "_" + substance + "_" + attribute_type)
        # value_span_eval_data[substance].output(ATTRIB_VALUE_SPAN_EVAL_FILENAME + "_" + substance + "_" + attribute_type)
        all_span_eval_data[substance].output(ATTRIB_ALL_SPAN_EVAL_FILENAME + "_" + substance + "_" + attribute_type)
        all_span_overlap_eval_data[substance].output(ATTRIB_ALL_SPAN_OVERLAP_EVAL_FILENAME + "_" + substance +
                                                     "_" + attribute_type)

    # Total across substances
    find_total_field_performance(value_eval_data, attribute, ATTRIB_VALUE_EVAL_FILENAME)
    # find_total_field_performance(value_span_eval_data, attribute, ATTRIB_VALUE_SPAN_EVAL_FILENAME)
    find_total_field_performance(all_span_eval_data, attribute, ATTRIB_ALL_SPAN_EVAL_FILENAME)
    find_total_field_performance(all_span_overlap_eval_data, attribute, ATTRIB_ALL_SPAN_OVERLAP_EVAL_FILENAME)
