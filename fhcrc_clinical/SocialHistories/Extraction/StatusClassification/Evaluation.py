from SystemUtilities.Configuration import *


def evaluate_doc_classifications(patients):
    fn_sents = {}   # {event type : [sentences]}
    fp_sents = {}   # {event type : [sentences]}
    tp = 0
    fn = 0
    fp = 0

    # Track sentences with errors for areas of improvement
    for event_type in ML_CLASSIFIER_SUBSTANCES:
        fn_sents[event_type] = []
        fp_sents[event_type] = []

    # TODO -- status eval
