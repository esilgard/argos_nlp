# extract and output substance information using the models trained in train_models.py
# output evaluation on test data or output results on unlabeled data
from DataLoading import DataLoader as DataLoader
from DataModeling.DataModels import *
from Evaluation import EventAndStatusEvaluate, AttributeEvaluate
from Postprocessing import postprocessing
from Extraction import PatientFromDocs, DocFromSents
from Extraction.AttributeExtraction import Execution as AttributeExtractionExec
from Extraction.EventDetection import Execution as EventDetectExecution
from Extraction.StatusClassification import Execution
from Extraction.EventAttributeLinking import Execution as EventFilling
from SystemUtilities import Shelver
from SystemUtilities.Configuration import *


def main(run_type=None, tsv_in=""):
    # #Set which division of data to use
    # DATA_SPLIT = "Test"
    #
    # print "Using data_dir: " + DATA_DIR
    # if run_type == "execute":
    #     patients = DataLoader.main("execute", tsv_in)
    #
    # # Load Data
    # else: # load data in either the test or train default configurations
    #     patients = DataLoader.main(DATA_SPLIT)
    #
    # #Shelver.shelve_patients(patients)
    # #patients = Shelver.unshelve_patients()
    #
    # # Determine sentence level info
    # extract_sentence_level_info(patients)

    #Shelver.shelve_full_patients(patients)
    patients = Shelver.unshelve_full_patients()

    # Determine document level info
    DocFromSents.get_doc_level_info(patients)

    # Determine patient level info
    PatientFromDocs.get_patient_level_info(patients)

    # Post-processing: sets of rules to clean up obvious contradictions
    postprocessing.clean_doc_lvl_predictions(patients)

    if ENV == RUNTIME_ENV.TEST:
        evaluate_extraction(patients)

    return patients


def extract_sentence_level_info(patients):
    # Find substance references
    print("Classifying substance references...")
    sentences_with_events = EventDetectExecution.detect_sentence_events(patients)

    # Classify substance status
    print("Classifying substance status...")
    Execution.classify_sentence_status(sentences_with_events)

    # Extract Attributes
    print("Extracting Attributes...")
    AttributeExtractionExec.extract(patients, stanford_ner_path=STANFORD_NER_PATH)

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
