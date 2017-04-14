import numpy

import test_pipeline
import train_pipeline
from DataLoading import DataLoader as DataLoader
from DataLoading.DataLoadingGlobals import FOLDS, FOLD5, FOLD4, FOLD3, FOLD2, FOLD1
from Evaluation import WEventAndStatusEvaluate, EventAndStatusEvaluate, AttributeEvaluate
from Extraction import PatientFromDocs, DocFromSents
from Extraction.AttributeExtraction import Execution_CRFSuite as AttributeExtractionExec
from Extraction.EventAttributeLinking import Execution as EventFilling
from Extraction.EventDetection import Execution as EventDetectExecution
from Extraction.StatusClassification import Execution
from SystemUtilities.Configuration import *


def print_crf_only_averages(crf_avg_dict):
    print ("============== K-Fold RESULTS ===========")
    print ("========= CRF PERFORMANCE -- AVERAGES: ==========")
    for key, values in crf_avg_dict.items():
        precisions = [x.precision for x in values]
        recalls = [x.recall for x in values]
        f1s = [x.f1 for x in values]

        mean_precision = numpy.mean(precisions)
        mean_recall = numpy.mean(recalls)
        mean_f1 = numpy.mean(f1s)

        print(key)
        print("\tP:"+ str(mean_precision))
        print("\tR:"+ str(mean_recall))
        print("\tF1:"+ str(mean_f1))


def print_attrib_assigned_averages(by_subs_avg_struct):
    print ("============== K-Fold RESULTS ===========")
    print ("========= CRF + Attrib Assignment PERFORMANCE -- AVERAGES: ==========")
    for key, values in by_subs_avg_struct.items():
        alc_precisions = [x["Alcohol"].precision for x in values]
        alc_recalls = [x["Alcohol"].recall for x in values]
        alc_f1s = [x["Alcohol"].f1 for x in values]
        tob_precisions =[x["Tobacco"].precision for x in values]
        tob_recalls = [x["Tobacco"].recall for x in values]
        tob_f1s = [x["Tobacco"].f1 for x in values]

        mean_alc_precision = numpy.mean(alc_precisions)
        mean_alc_recall = numpy.mean(alc_recalls)
        mean_alc_f1 = numpy.mean(alc_f1s)
        mean_tob_precision = numpy.mean(tob_precisions)
        mean_tob_recall = numpy.mean(tob_recalls)
        mean_tob_f1 = numpy.mean(tob_f1s)

        print(key + "Alcohol")
        print("\tP:" + str(mean_alc_precision))
        print("\tR:" + str(mean_alc_recall))
        print("\tF1:" + str(mean_alc_f1))
        print(key + "Tobacco")
        print("\tP:" + str(mean_tob_precision))
        print("\tR:" + str(mean_tob_recall))
        print("\tF1:" + str(mean_tob_f1))


def print_result_avgs(fold_results):
    by_subs_avg_struct = dict()
    crf_avg_struct= dict()
    for i in range(len(fold_results)):
        for result_type, result_obj in fold_results[i].items():
            if "bySubstance" in result_type:
                if result_type not in by_subs_avg_struct:
                    by_subs_avg_struct[result_type] = list()
                by_subs_avg_struct[result_type].append(result_obj)
            elif "CRFOnly" in result_type:
                if result_type not in crf_avg_struct:
                    crf_avg_struct[result_type] = list()
                crf_avg_struct[result_type].append(result_obj)
    print_crf_only_averages(crf_avg_struct)
    print_attrib_assigned_averages(by_subs_avg_struct)


def main():
    print "Using data_dir: " + DATA_DIR
    fold_results = list()
    for i in range(len(FOLDS)):
        # compile training set from all folds minus current
        list_of_sets=list()
        [list_of_sets.append(x) for x in FOLDS if FOLDS[i] != x]
        training_set = set()
        for s in list_of_sets:
            training_set.update(s)
        # Train on training set
        train_pipeline.main(training_set)
        # Test on current set
        results = test_pipeline.main(FOLDS[i])
        fold_results.append(results)

    # do something with fold results (get avgs)
    print print_result_avgs(fold_results)


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
    WEventAndStatusEvaluate.evaluate_event_detection(patients)

    # Status classification
    WEventAndStatusEvaluate.evaluate_status_classification(patients)

    # Extraction of each attribute
    results = AttributeEvaluate.evaluate_attributes(patients)

    # Event-Attribute linking?

    # Template?

    return results

if __name__ == '__main__':
    patient_substance_info = main()
