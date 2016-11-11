# extract and output substance information using the models trained in train_models.py
# output evaluation on test data or output results on unlabeled data
from DataLoading import DataLoader as DataLoader
from Evaluation import EventAndStatusEvaluate, AttributeEvaluate
from Postprocessing import postprocessing
from Extraction import PatientFromDocs, DocFromSents
from Extraction.AttributeExtraction import Execution_CRFSuite as AttributeExtractionExec
from Extraction.EventDetection import Execution as EventDetectExecution
from Extraction.StatusClassification import Execution
from Extraction.EventAttributeLinking import Execution as EventFilling
from SystemUtilities.Configuration import *


def main(run_type=None, tsv_in=""):
    print "Using data_dir: " + DATA_DIR
    patients = DataLoader.main(tsv_in)
    # Determine sentence level info
    extract_sentence_level_info(patients)
    # Determine document level info
    DocFromSents.get_doc_level_info(patients)
    # Determine patient level info
    PatientFromDocs.get_patient_level_info(patients)
    # Post-processing: sets of rules to clean up obvious contradictions
    postprocessing.clean_doc_lvl_predictions(patients)
    return patients


def extract_sentence_level_info(patients):
    # Find substance references
    print("Classifying substance references...")
    sentences_with_events = EventDetectExecution.detect_sentence_events(patients)
    print("\t" + str(len(sentences_with_events)) + " sentences with events found")
    # Classify substance status
    print("Classifying substance status...")
    Execution.classify_sentence_status(sentences_with_events)
    # Extract Attributes
    print("Extracting Attributes...")
    AttributeExtractionExec.extract(patients)
    # Link attributes to events:
    print("Linking attributes to substance references...")
    EventFilling.link_attributes_to_substances(patients)


def evaluate_extraction(patients):
    # Event detection
    EventAndStatusEvaluate.evaluate_event_detection(patients)

    # Status classification
    EventAndStatusEvaluate.evaluate_status_classification(patients)

    # Extraction of each attribute
    AttributeEvaluate.evaluate_attributes(patients)

    # Event-Attribute linking?

    # Template?


if __name__ == '__main__':
    patient_substance_info = main()
