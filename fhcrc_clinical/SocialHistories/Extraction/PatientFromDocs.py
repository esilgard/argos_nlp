from SystemUtilities.Globals import *
from DataModeling.DataModels import Event, PatientAttribute


def get_patient_level_info(patients):

    for patient in patients:
        # Get events
        find_patient_events(patient)

        # Get status
        get_patient_status(patient)

        # Get each attribute
        get_patient_attributes(patient)


def find_patient_events(patient):
    substances_in_docs = substances_found_in_docs(patient)

    for substance in substances_in_docs:
        patient.predicted_events.append(Event(substance))


def substances_found_in_docs(patient):
    substances_in_docs = set()
    for doc in patient.doc_list:
        for event in doc.predicted_events:
            substances_in_docs.add(event.substance_type)
    return substances_in_docs


def get_patient_status(patient):
    for pred_event in patient.predicted_events:
        chronological_docs = sort_docs_chronologically(patient.doc_list)
        pred_event.status = get_patient_subst_status(chronological_docs, pred_event.substance_type)


def sort_docs_chronologically(doc_list):
    sorted_docs = []
    # TODO -- sort_docs_chronologically to find patient status
    return doc_list


def get_patient_subst_status(docs, substance):
    """ Recursively descend through chronologically sorted docs to determine patient level status by reasoning
    based on doc level statuses"""
    doc_status = current_doc_status(docs, substance)
    previous_docs = docs[1:]

    if doc_status in POSITIVE_STATUSES or not previous_docs:
        patient_status = doc_status
    else:
        patient_status = patient_status_if_current_doc_non_or_unk(doc_status, previous_docs, substance)

    return patient_status


def current_doc_status(docs, substance):
    doc_status = UNKNOWN
    for event in docs[0].gold_events:
        if event.substance_type == substance:
            doc_status = event.status
    return doc_status


def patient_status_if_current_doc_non_or_unk(doc_status, previous_docs, substance):
    previous_status = get_patient_subst_status(previous_docs, substance)

    if doc_status == NON:
        if previous_status in POSITIVE_STATUSES:
            patient_status = FORMER
        else:
            patient_status = NON

    else:  # doc_status == UNKNOWN
        patient_status = previous_status

    return patient_status


def get_patient_attributes(patient):

    for patient_event in patient.predicted_events:
        substance = patient_event.substance_type

        # get all document attributes for each field
        all_doc_attribs, doc_ids = get_attributes_for_all_docs(patient, substance)

        # create patient level attributes from doc attributes
        create_patient_attributes(all_doc_attribs, doc_ids, patient_event)


def get_attributes_for_all_docs(patient, substance):
    all_doc_attribs = {field: [] for field in ATTRIBS[substance]}   # All DocumentAttribute objects for field
    doc_ids = {field: [] for field in ATTRIBS[substance]}           # Track document ids for each object

    for doc in patient.doc_list:
        for doc_event in doc.predicted_events:
            if doc_event.substance_type == substance:
                for attrib in doc_event.attributes:
                    all_doc_attribs[attrib].append(doc_event.attributes[attrib])
                    doc_ids[attrib].append(doc.id_num)

    return all_doc_attribs, doc_ids


def create_patient_attributes(all_doc_attribs, all_doc_ids, patient_event):
    for field in all_doc_attribs:
        doc_attribs = all_doc_attribs[field]
        doc_ids = all_doc_ids[field]

        if doc_attribs:
            # Choose the value for the paitent level field
            selected_attrib, doc_id = select_patient_field_value(doc_attribs, doc_ids)

            # Create the patient attribute
            patient_event.attributes[field] = PatientAttribute(field, selected_attrib.span_start,
                                                               selected_attrib.span_stop, selected_attrib.text, doc_id,
                                                               doc_attribs, doc_ids)


def select_patient_field_value(doc_attribs, doc_ids):
    selected_attrib = doc_attribs[0]
    doc_id = doc_ids[0]
    for attrib, doc_id in zip(doc_attribs, doc_ids):
        # TODO -- select patient level attribute from doc level
        pass

    return selected_attrib, doc_id
