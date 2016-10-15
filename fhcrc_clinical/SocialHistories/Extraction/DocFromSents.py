from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import STATUS_HIERARCHY, UNKNOWN, entity_types
from fhcrc_clinical.SocialHistories.Extraction.EventAttributeLinking import Execution as EventFilling
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import DocumentEvent, DocumentAttribute, Span


def get_doc_level_info(patients):
    for patient in patients:
        for doc in patient.doc_list:
            # make doc events
            find_doc_events(doc)

            # doc status
            get_doc_level_status(doc)

            # roll sentence-level events to doc level
            sentence_events_to_doc_level(doc)

            # attributes
            EventFilling.attributes_to_doc_level(doc)


def find_doc_events(doc):
    substances_in_docs = substances_found_in_sents(doc)

    for substance in substances_in_docs:
        doc.predicted_events.append(DocumentEvent(substance))


def substances_found_in_sents(doc):
    substances_in_docs = set()
    for sent in doc.sent_list:
        for event in sent.predicted_events:
            substances_in_docs.add(event.substance_type)
    return substances_in_docs


def get_doc_level_status(doc):
    """ Get document level status from sentence level statuses """
    for doc_event in doc.predicted_events:
        substance = doc_event.substance_type

        sentence_level_statuses = get_sent_level_statuses_for_doc(doc, substance)
        doc_status, spans = doc_level_status(sentence_level_statuses)

        doc_event.status = doc_status
        doc_event.status_spans = spans

    # Remove events who's predicted status is unknown
    new_predicted_events = list()
    for doc_event in doc.predicted_events:
        if doc_event.status != UNKNOWN:
            new_predicted_events.append(doc_event)
    doc.predicted_events = new_predicted_events


def get_sent_level_statuses_for_doc(doc, substance):
    """ Get all values of status in the doc's sentences for the given substance """
    sentence_level_statuses = dict()

    for sent in doc.sent_list:
        for event in sent.predicted_events:
            if event.substance_type == substance:
                if event.status not in sentence_level_statuses:
                    sentence_level_statuses[event.status] = list()
                sentence_level_statuses[event.status].append((sent.span_in_doc_start, sent.span_in_doc_end))

    return sentence_level_statuses


def doc_level_status(sentence_level_statuses):
    doc_status = UNKNOWN
    spans = []

    # Go through precedence-ordered list of statuses and take the first one found
    for status in STATUS_HIERARCHY:
        if status in sentence_level_statuses:
            doc_status = status
            spans = convert_tupleSpans_to_SpanObjs(sentence_level_statuses[status])
            break

    return doc_status, spans


def sentence_events_to_doc_level(doc):
    all_attributes_for_field = {}
    for sentence in doc.sent_list:
        if len(sentence.sentence_attribs) > 0:
            for attrib in sentence.sentence_attribs:
                if attrib.type not in all_attributes_for_field:
                    all_attributes_for_field[attrib.type] = []
                all_attributes_for_field[attrib.type].append(attrib)

    # Unintelligently pick the first of each type to be the official Document-level attribute
    for attrib_field_key in sorted(all_attributes_for_field.keys()):
        attrib_list = all_attributes_for_field[attrib_field_key]
        official_attrib_type = attrib_list[0].type
        offcial_attrib_start = attrib_list[0].span_start
        official_attrib_end = attrib_list[0].span_end
        official_attrib_text = attrib_list[0].text
        official_attrib_probability = attrib_list[0].probability
        doc_attrib = DocumentAttribute(official_attrib_type, offcial_attrib_start, official_attrib_end, official_attrib_text, attrib_list, official_attrib_probability)

        doc.all_attributes[attrib_field_key] = doc_attrib

def convert_tupleSpans_to_SpanObjs(list_of_tuple_spans):
    spans = list()
    for tuple_span in list_of_tuple_spans:
        spans.append(Span(tuple_span[0], tuple_span[1]))
    return spans