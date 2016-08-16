from SystemUtilities.Configuration import *
import Processing
from Extraction import Classification
from DataModeling.DataModels import DocumentAttribute


def link_attributes_to_substances(doc):
    classifier, feature_map = load_event_filling_classifier()

    # Find all values for all fields for all substances
    attributes_per_substance = find_attributes_per_substance(classifier, feature_map, doc)

    # Put the appropriate values into doc objects
    put_attributes_in_doc_events(doc, attributes_per_substance)


def load_event_filling_classifier():
    classifier_file = MODEL_DIR + EVENT_FILLER_MODEL_NAME
    feature_map_file = MODEL_DIR + EVENT_FILLER_FEATMAP_NAME

    classifier, feature_map = Classification.load_classifier(classifier_file, feature_map_file)
    return classifier, feature_map


def find_attributes_per_substance(classifier, feature_map, doc):
    """ Get all attributes assigned to each substance -- {substance: field: [Attributes]} """
    attribs_found_per_substance = {subst: {field: [] for field in ATTRIBS[subst]} for subst in SUBSTANCE_TYPES}

    # Get features
    attrib_feature_sets, attributes = Processing.features(doc)

    # Get classifications
    for attrib, features in zip(attributes, attrib_feature_sets):
        classifications = Classification.classify_instance(classifier, feature_map, features)

        # Assign attribute to substance identified
        classified_substance = classifications[0]
        if classified_substance in SUBSTANCE_TYPES:
            attribs_found_per_substance[classified_substance].append(attrib)

    return attribs_found_per_substance


def put_attributes_in_doc_events(doc, attribs_per_substance):
    """ doc.attributes = {attribute_name: DocumentAttribute} """
    for event in doc.predicted_events:
        for attribute_name in attribs_per_substance[event.substance_type]:
            all_values_for_field = attribs_per_substance[event.substance_type][attribute_name]
            if all_values_for_field:
                event.attributes[attribute_name] = create_document_attribute(all_values_for_field)


def create_document_attribute(all_values_for_field):
    # Choose document level value
    selected_value = select_doc_value_from_all_values(all_values_for_field)

    # Create document level attribute object
    document_attribute = DocumentAttribute(selected_value.type, selected_value.span_start, selected_value.span_end,
                                           selected_value.text, all_values_for_field)

    return document_attribute


def select_doc_value_from_all_values(all_attributes):
    # TODO -- better selection criteria: prefer by precision then prefer by amount
    selected_value = all_attributes[0]
    return selected_value
