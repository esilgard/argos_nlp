from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import *
import Processing
from fhcrc_clinical.SocialHistories.Extraction import Classification
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import DocumentAttribute
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *


def link_attributes_to_substances(patients):
    classifier, feature_map = load_event_filling_classifier()

    for patient in patients:
        for doc in patient.doc_list:
            previous_sent = None
            for sent in doc.sent_list:
                # Find all values for all fields for all substances
                attributes_per_substance = find_attributes_per_substance(classifier, feature_map, sent, previous_sent)

                # Put the appropriate values into doc objects
                put_attributes_in_sent_events(sent, attributes_per_substance)

                previous_sent = sent


def load_event_filling_classifier():
    classifier_file = os.path.join(MODEL_DIR, EVENT_FILLER_MODEL_NAME)
    feature_map_file = os.path.join(MODEL_DIR, EVENT_FILLER_FEATMAP_NAME)

    classifier, feature_map = Classification.load_classifier(classifier_file, feature_map_file)
    return classifier, feature_map


def find_attributes_per_substance(classifier, feature_map, sent, previous_sent):
    """ Get all attributes assigned to each substance -- {substance: field: [Attributes]} """
    attribs_found_per_substance = {subst: {} for subst in SUBSTANCE_TYPES}

    # Get features
    attrib_feature_sets, attributes = Processing.features(sent, previous_sent)

    # Get classifications
    for attrib, features in zip(attributes, attrib_feature_sets):

        # If there is only one substance for the type of attribute, just assign to that substance
        if attrib.type in KNOWN_SUBSTANCE_ATTRIBS:
            add_attrib_with_known_substance(attribs_found_per_substance, attrib)

        # Else, use machine learning classifier
        else:
            add_attrib_using_classifier(classifier, feature_map, features, attribs_found_per_substance, attrib)

    return attribs_found_per_substance


def add_attrib_with_known_substance(attribs_found_per_substance, attrib):
    """ For an attribute that can only be one substance, simply assign to that substance """
    substance = KNOWN_SUBSTANCE_ATTRIBS[attrib.type]

    if attrib.type not in attribs_found_per_substance[substance]:
        attribs_found_per_substance[substance][attrib.type] = []

    attribs_found_per_substance[substance][attrib.type].append(attrib)


def add_attrib_using_classifier(classifier, feature_map, features, attribs_found_per_substance, attrib):
    """ For an attribute that can be different substances, using ML classifier """
    classifications = Classification.classify_instance(classifier, feature_map, features)

    # Assign attribute to substance identified
    classified_substance = classifications[0]
    if classified_substance in SUBSTANCE_TYPES:

        if attrib.type not in attribs_found_per_substance[classified_substance]:
            attribs_found_per_substance[classified_substance][attrib.type] = []

        attribs_found_per_substance[classified_substance][attrib.type].append(attrib)


def put_attributes_in_sent_events(sent, attribs_per_substance):
    """ For each event in sent, event.attributes is set to {attribute_name: [Attribute]}.
     @type: attribs_per_substance = {substance: field: [Attribute]}"""
    sent.attributes_per_substance = attribs_per_substance

    for event in sent.predicted_events:
        for attribute_name in attribs_per_substance[event.substance_type]:
            all_values_for_field = attribs_per_substance[event.substance_type][attribute_name]
            if all_values_for_field:
                event.attributes[attribute_name] = all_values_for_field


def attributes_to_doc_level(doc):
    """@type: doc = Document"""
    doc_attribs_per_substance = {subst: {} for subst in SUBSTANCE_TYPES}

    # Create a document attribute object from sentence attributes
    for sent in doc.sent_list:
        for event in sent.predicted_events:
            for attrib_name, attrib_list in event.attributes.items():
                doc_attribute = create_document_attribute(attrib_list, sent.span_in_doc_start)
                doc_attribs_per_substance[event.substance_type][attrib_name] = doc_attribute

    # Add doc attribs to doc object
    for event in doc.predicted_events:
        for attrib_name, attrib_obj in doc_attribs_per_substance[event.substance_type].items():
            event.attributes[attrib_name] = attrib_obj


def create_document_attribute(all_values_for_field, span_in_doc_start):
    # Choose document level value
    selected_value, all_values_for_field = select_doc_value_from_all_values(all_values_for_field, span_in_doc_start)

    # Create document level attribute object
    document_attribute = DocumentAttribute(selected_value.type, selected_value.span_start, selected_value.span_end,
                                           selected_value.text, all_values_for_field, selected_value.probability)

    return document_attribute


def select_doc_value_from_all_values(all_attributes, span_in_doc_start):
    """@type all_attributes: List(Attribute) """
    # Add index within document to index within sentence
    for attrib in all_attributes:
        attrib.span_start += span_in_doc_start
        attrib.span_end += span_in_doc_start

    # TODO -- better selection criteria: prefer by precision then prefer by amount
    selected_value = all_attributes[0]
    return selected_value, all_attributes
