"""The ServerQuery is only used to import data for training and testing. This Labkey-based NLP
pipeline is only concerned with the execution pipeline, which takes new data as input. This module is therefore
obsolete in this context and had to be commented out because it has dependencies which are not installed on
the Labkey Server environments."""

import labkey
import re
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import *
from DataLoadingGlobals import *


def get_annotations_from_server():
    """
    :return: {annotator_id: {MRN: {doc_id: [Event]}}} -- the list of events has one gold Event for each substance
    """
    print ("Creating Labkey server context ...")
    context = labkey.utils.create_server_context(SERVER, PROJECT, use_ssl=True)

    all_fields = labkey.query.select_rows(
        server_context=context,
        schema_name='nlp',
        query_name='FieldResult'
    )

    all_offsets = labkey.query.select_rows(
        server_context=context,
        schema_name='nlp',
        query_name='startStopPosition'
    )

    reports = labkey.query.select_rows(
        server_context=context,
        schema_name='nlp',
        query_name='report'
    )

    # Grab relevant fields and offsets for each annotator
    field_results_per_annotr = field_query_results(all_fields)
    offset_results_per_annotr = offset_query_results(all_offsets, field_results_per_annotr)

    patient_doc_annotations = fill_annotation_objects(field_results_per_annotr, offset_results_per_annotr, reports)
    return patient_doc_annotations


def field_query_results(all_fields):
    """ Get every field for each annotator """
    field_results_per_annotator = {}  # {annotator_id: [social history rows]}

    filtered_fields = filter_fields(all_fields)

    # Find fields per annotator
    for field in filtered_fields:
        annotator = field[CREATED_BY]
        if annotator not in field_results_per_annotator:
            field_results_per_annotator[annotator] = []
        field_results_per_annotator[annotator].append(field)

    return field_results_per_annotator


def offset_query_results(all_offsets, field_results_per_annotator):
    """ Get the text spans for every field for each annotator """
    offset_results_per_annotator = {annotator: [] for annotator in field_results_per_annotator}
    for annotator in offset_results_per_annotator:
        offset_results_per_annotator[annotator] = [o for o in all_offsets[ROWS] if (o[CREATED_BY] == annotator)]

    return offset_results_per_annotator


def find_fields(field_results, offset_results):
    fields, field_names_per_report = create_field_objects(field_results)
    add_field_offsets(fields, offset_results)
    fields_per_report = find_fields_per_report(fields, field_names_per_report)
    return fields_per_report


def create_field_objects(field_data):
    fields = {}                 # {field_id: Field}
    fields_per_report = {}      # {report_id: [field_id]}
    for field in field_data:
        field_id = field[FIELD_ID]
        field_obj = Field(field[FIELD_NAME], field[VALUE])

        fields[field_id] = field_obj
        update_fields_per_report(field, field_id, fields_per_report)

    return fields, fields_per_report


def update_fields_per_report(field, field_id, fields_per_report):
    report_id = field[REPORT_ID]
    if report_id not in fields_per_report:
        fields_per_report[report_id] = []
    fields_per_report[report_id].append(field_id)


def add_field_offsets(fields, offset_results):
    for offset in offset_results:
        field_id = offset[FIELD_ID]
        if field_id in fields:
            span = Span(offset[START_POS], offset[STOP_POS])
            fields[field_id].spans.append(span)


def find_fields_per_report(fields, field_names_per_report):
    fields_per_report = {}  # {report_id: [Field objects]}
    for report_id in field_names_per_report:
        fields_per_report[report_id] = []

        for field_id in field_names_per_report[report_id]:
            fields_per_report[report_id].append(fields[field_id])

    return fields_per_report


def convert_fields_to_substance_events(fields_per_report):
    substances_of_fields = find_substances_of_fields()

    events_per_report = {}
    for report_id in fields_per_report:
        events_per_report[report_id] = create_events()
        fill_events(fields_per_report, report_id, substances_of_fields, events_per_report)

    return events_per_report


def find_substance_field_names():
    """ Find the set of LabKey field names for each substance type """
    fields_per_subst = {}
    for subst in SUBSTANCE_TYPES:
        # Status
        status = subst + STATUS
        fields_per_subst[subst] = {status}

        # Substance-specific attributes
        for attrib in ATTRIBS[subst]:
            attrib_label = subst + attrib
            fields_per_subst[subst].add(attrib_label)

    return fields_per_subst


def find_substances_of_fields():
    substance_per_field_name = {}
    for subst in SUBSTANCE_TYPES:
        # Status
        status = subst + STATUS
        substance_per_field_name[status] = subst

        # Attributes
        for attrib in ATTRIBS[subst]:
            attrib_label = subst + attrib
            substance_per_field_name[attrib_label] = subst

    return substance_per_field_name


def create_events():
    events = {}
    for substance in SUBSTANCE_TYPES:
        events[substance] = DocumentEvent(substance)
    return events


def fill_events(fields_per_report, report_id, substances_of_fields, events_per_report):
    fields = fields_per_report[report_id]
    for field in fields:
        if field.name in substances_of_fields:
            substance = substances_of_fields[field.name]
            add_field_to_event(field, substance, events_per_report[report_id][substance])


def add_field_to_event(field, substance, event):
    # Get rid of "Alcohol", "Tobacco", etc
    field_name = re.sub(substance, "", field.name)

    if field_name == STATUS:
        event.status = field.value
        event.status_spans = field.spans
    elif field_name in ATTRIBS[substance]:
        event.attributes[field_name] = AnnotatedAttribute(field_name, field.spans, field.value)


def match_reports_to_patients(events_per_report, all_reports):
    doc_events_per_patient = {annotator: {} for annotator in events_per_report}  # {annotator: {mrn: {doc: [Event]}}}
    reports = [r for r in all_reports[ROWS] if r[JOB_ID] in JOB_IDS]

    for report in reports:
        add_events_to_patient(report, report[REPORT_ID], events_per_report, doc_events_per_patient)

    return doc_events_per_patient


def add_events_to_patient(report, report_id, events_per_report, doc_events_per_patient):
    mrn = report[MRN]
    doc_id = report[DOC_ID]
    annotator = report[MODIFIED_BY]

    if annotator in doc_events_per_patient:
        if mrn not in doc_events_per_patient[annotator]:
            doc_events_per_patient[annotator][mrn] = {}

        # Add events
        if report_id in events_per_report[annotator]:
            # Add filled events
            doc_events_per_patient[annotator][mrn][doc_id] = events_per_report[annotator][report_id]
        else:
            # Add empty events
            doc_events_per_patient[annotator][mrn][doc_id] = create_events()


def fill_annotation_objects(field_results_per_annotator, offset_results_per_annotator, reports):
    """ Go through fields for each annotator and group the fields currently jumbled together into their respective
    documents and group documents by MRN """
    print ("Finding events per report (ServerQuery.py ln219) ...")
    events_per_report = find_events_per_report(field_results_per_annotator, offset_results_per_annotator)
    print ("Matching reports to patients (ServerQuery.py ln221)...")
    patient_doc_annotations = match_reports_to_patients(events_per_report, reports)
    print("\tFinished matching ...")
    return patient_doc_annotations


def find_events_per_report(field_results_per_annotator, offset_results_per_annotator):
    events_per_report = {annotator: {} for annotator in field_results_per_annotator}
    for annotator in field_results_per_annotator:
        fields_per_report = find_fields(field_results_per_annotator[annotator], offset_results_per_annotator[annotator])
        events_per_report[annotator] = convert_fields_to_substance_events(fields_per_report)
    return events_per_report


def filter_fields(all_fields):
    # by job run ID
    right_job_id_fields = [f for f in all_fields[ROWS] if f[REPORT_JOB_ID] in JOB_IDS]

    # by SocialHistory table
    soc_history_fields = [f for f in right_job_id_fields if (f[u'TargetTable'] == SOC_HISTORIES)]

    return soc_history_fields
