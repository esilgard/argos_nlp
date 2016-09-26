def clean_doc_lvl_predictions(patients):
    ''' Break down and process on a doc-by-doc basis '''
    for patient in patients:
        for document in patient.doc_list:
            process_document(document)
    pass


def process_document(document):
    ''' Individual docs get sent through a gauntlet of post-processing tasks as needed '''
    map_subs_type_to_closed_class(document)
    pass


def map_subs_type_to_closed_class(document):
    ''' Mapping tobacco type to closed class of {smoke, smokeless} right now consists
    of the logic "if a type was detected, we are going to assume it was smoke because it is
    by far the largest class" '''
    for predicted_event in document.predicted_events:
        if len(predicted_event.attributes) != 0:
            if "Type" in predicted_event.attributes:
                predicted_event.attributes["Type"].text = "smoke"
    pass