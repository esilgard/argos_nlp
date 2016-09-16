# Contains tunable system parameters
import os

from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *

# User-specific configuration
USER = will

# Environment/run type
ENV = RUNTIME_ENV.TEST

# User-specific paths
gold_annotation_dir = ""

# if USER == spencer:
#     data_dir = "C:\Users\sdmorris\Documents\FHCRC\ExposureProject\Substance_IE_Data\\"
#     florian_dir = r"C:\Users\sdmorris\Documents\FHCRC\Resources\Florian\Florian_smoking\smoking_status\\"
#     RAW_DATA_DIR = data_dir + r"exposure_notes.txt"
#     METADATA_DIR = data_dir + r"metadata_for_clinic_notes.xlsx"
#     CAISIS_DIR = data_dir + r"caisis_exposure_labels.xlsx"
#     NOTE_OUTPUT_DIR = data_dir + r"SystemOutput\Notes\\"
#     TRAIN_SPLIT_DIR = data_dir + r"notes_training\\"
#     DEV_SPLIT_DIR = data_dir + r"notes_dev\\"
#     TEST_SPLIT_DIR = data_dir + r"notes_testing\\"
#     NOTE_OUTPUT_GOLD_LABELS_DIR = r"SystemOutput\Notes_annotations\\"
#     MODEL_DIR = data_dir + r"SystemOutput\Models\\"
#     # GOLD annotation sources
#     gold_annotation_dir = florian_dir + r"SmokingStatusAnnotator\resources\gold\\"
#     # Data sources
#     data_repo_dir = florian_dir + r"sortedNotes\sortedNotes\combined\\"
#     dev_csv = data_dir + r"FLOR_filtered_tsv\flor_dev.csv"
#     test_csv = "C:\Users\wlane\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_test.csv"
#     train_csv = "C:\Users\wlane\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_train.csv"
#     ADJUDICATED_BATCH_0 = data_dir + r"SystemOutput\adj_batch_0.p"
#     flors_sent_level_annotations_dir = data_dir + r"sentence_level_annotations.json"
#     # Output files
#     SUBSTANCE_IE_DATA_FOLDER = data_dir
#     FLORIAN_FULL_DATA = florian_dir + r"sortedNotes\sortedNotes\combined\\"
#     METADATA_OUT = data_dir + r"SystemOutput\Metadata"
#     DOCS_NEEDING_ANNOTATION_DIR = data_dir + r"SystemOutput\DocsToAnnotate\\"
#     # Evaluation
#     SENT_EVENT_DETECT_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\EventDetection\SentEventDetectionEval"
#     DOC_EVENT_DETECT_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\EventDetection\DocEventDetectionEval"
#     SENT_STATUS_CLASSF_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\SentStatusClassificationEval"
#     DOC_STATUS_CLASSF_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\DocStatusClassificationEval"
#     ATTRIB_VALUE_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\AttributeValues\AttribValueEval"
#     ATTRIB_VALUE_SPAN_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\AttributeValueSpans\AttribValueSpanEval"
#     ATTRIB_ALL_SPAN_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\AttributeSpans\AttribAllSpanEval"
#     ATTRIB_ALL_SPAN_OVERLAP_EVAL_FILENAME = data_dir + r"SystemOutput\Evaluation\AttributeSpansOverlap\AttribAllSpanOverlapEval"
#     # IAA
#     IAA_DISAGREEMENT_LOG = data_dir + "SystemOutput\IAA\disagreement_log.tsv"
#     SPAN_DISAGREEMENT_LOG = data_dir + "SystemOutput\IAA\span_disagreement_log.tsv"
#     IAA_OUT_FILE = data_dir + "SystemOutput\IAA\IAA.txt"
#     ADJUDICATION_DIR = data_dir + r"adjudication.xlsx"
#     # Stanford Tools
#     STANFORD_NER_PATH = r"C:\Users\sdmorris\StanfordNER\stanford-ner-2015-12-09\stanford-ner.jar"
#     STANFORD_NER_LIB_ALL = r"C:\Users\sdmorris\StanfordNER\stanford-ner-2015-12-09\lib\*"
#     ATTRIB_EXTRACTION_DIR_HOME = r"C:\\Users\\sdmorris\\Documents\\FHCRC\\ExposureProject\\Substance_IE_Data\\SystemOutput\\NER\\"

if USER == will:
    data_dir = os.path.join('/home', 'wlane', 'Documents', 'Substance_IE_Data', '')
    METADATA_DIR = r"C:\Users\wlane\Documents\Substance_IE_Data\resources\metadata_partdeux.xlsx"
    CAISIS_DIR = r"/home/wlane/Documents/Substance_IE_Data/resources/caisis_exposure_labels.xlsx"
    NOTE_OUTPUT_DIR = r"/home/wlane/Documents/Substance_IE_Data/output/"
    TRAIN_SPLIT_DIR =  r"C:\Users\wlane\Documents\Substance_IE_Data\notes_training\\"
    DEV_SPLIT_DIR = r"C:\Users\wlane\Documents\Substance_IE_Data\notes_dev"
    TEST_SPLIT_DIR = r"C:\Users\wlane\Documents\Substance_IE_Data\notes_testing\\"
    NOTE_OUTPUT_GOLD_LABELS_DIR = r"C:\Users\wlane\Documents\Substance_IE_Data\output_annotations\\"
    MODEL_DIR = data_dir + os.path.sep + "resources" +os.path.sep + "Models" + os.path.sep
    # GOLD annotation sources
    gold_annotation_dir = r"/home/wlane/Documents/Substance_IE_Data/resources/Florian_Data/Florian/smoking_status/SmokingStatusAnnotator/resources/gold/"
    # Data sources
    data_repo_dir = r"C:\Users\wlane\Documents\Substance_IE_Data\output\\"
    dev_csv = "C:\Users\wlane\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_dev.csv"
    test_csv = "C:\Users\wlane\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_test.csv"
    train_csv = "C:\Users\wlane\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_train.csv"
    flors_sent_level_annotations_dir = data_dir+ "/resources/Florians_sentence_level_annotations/sentence_level_annotations.json"
    # Output files
    SUBSTANCE_IE_DATA_FOLDER = data_dir
    FLORIAN_FULL_DATA = "/home/wlane/Documents/Substance_IE_Data/resources/Florian_Data/sortedNotes/all/"
    DOCS_NEEDING_ANNOTATION_DIR =  r"C:\Users\wlane\Documents\Substance_IE_Data\Docs_to_annotate\\"
    # Evaluation
    SENT_STATUS_CLASSF_EVAL_FILENAME =data_dir + os.sep + "Evaluation" + os.sep + "SentStatusClassificationEval"
    DOC_STATUS_CLASSF_EVAL_FILENAME = data_dir + os.sep + "Evaluation" + os.sep+ "DocStatusClassificationEval"
    SENT_EVENT_DETECT_EVAL_FILENAME = data_dir + os.sep + "Evaluation" + os.sep +"SentEventDetectionEval"
    DOC_EVENT_DETECT_EVAL_FILENAME = data_dir + os.sep + "Evaluation" + os.sep + "DocEventDetectionEval"
    ATTRIB_VALUE_EVAL_FILENAME = data_dir + r"Evaluation" +os.sep+"AttribValueEval"
    ATTRIB_VALUE_SPAN_EVAL_FILENAME = data_dir + r"Evaluation" +os.sep+"AttribValueSpanEval"
    ATTRIB_ALL_SPAN_EVAL_FILENAME = data_dir + r"Evaluation" +os.sep+"AttribAllSpanEval"
    ATTRIB_ALL_SPAN_OVERLAP_EVAL_FILENAME = data_dir + r"Evaluation" +os.sep+"AttribAllSpanOverlapEval"
    # IAA
    IAA_DISAGREEMENT_LOG = data_dir + "disagreement_log.txt"
    IAA_OUT_FILE = data_dir + "IAA.txt"
    IAA_OUT_FILE = data_dir + "_____WILLLS SOMETHKING ______________"
    ADJUDICATION_DIR = data_dir + r"_____WWILLLLS SOMETHIGN______________"
    # Stanford tools
    STANFORD_NER_PATH = data_dir + "stanford-ner-2015-12-09/stanford-ner.jar"
    STANFORD_NER_LIB_ALL = data_dir + "stanford-ner-2015-12-09/lib/*:"
    ATTRIB_EXTRACTION_DIR_HOME = data_dir + "AttributeExtractionModels/"
elif USER == emily:
    data_dir = r"C:\Users\esilgard\Documents\Substance_IE_Data\\"
    RAW_DATA_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\resources\exposure_notes_utf8.txt"
    METADATA_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\resources\metadata_partdeux.xlsx"
    CAISIS_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\resources\caisis_exposure_labels.xlsx"
    NOTE_OUTPUT_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\output\\"
    TRAIN_SPLIT_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\notes_training\\"
    DEV_SPLIT_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\notes_dev"
    TEST_SPLIT_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\notes_testing\\"
    NOTE_OUTPUT_GOLD_LABELS_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\output_annotations\\"
    MODEL_DIR = "C:\Users\esilgard\Documents\Substance_IE_Data\\resources\Models\\"
    ## GOLD annotation sources
    gold_annotation_dir = r"C:\Users\esilgard\Documents\Florian_smoking\smoking_status\SmokingStatusAnnotator\resources\gold\\"

    ## Data sources
    data_repo_dir = r"C:\Users\esilgard\Documents\Substance_IE_Data\output\\"
    dev_csv = "C:\Users\esilgard\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_dev.csv"
    test_csv = "C:\Users\esilgard\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_test.csv"
    train_csv = "C:\Users\esilgard\Documents\Substance_IE_Data\FLOR_filtered_tsv\\flor_train.csv"
    # Output files
    SENT_EVENT_DETECT_EVAL_FILENAME = r"C:\User_____eval folder here ______on\EventDetectionEval.txt"
    SUBSTANCE_IE_DATA_FOLDER = r"C:\Users\esilgard\Documents\Substance_IE_Data\\"
    FLORIAN_FULL_DATA = "C:\Users\esilgard\Documents\Florian_smoking\smoking_status\\full_data_set\\"
    DOCS_NEEDING_ANNOTATION_DIR = r"C:\Users\esilgard\Documents\Substance_IE_Data\Docs_to_annotate\\"
    # IAA
    IAA_DISAGREEMENT_LOG = r"C:\Users\esilgard\Documents\Substance_IE_Data\disagreement_log.txt"
    IAA_OUT_FILE = r"C:\Users\esilgard\Documents\Substance_IE_Data\IAA.txt"
    # Stanford Tools
    STANFORD_NER_PATH = "put path to stanford NER here"
    STANFORD_NER_LIB_ALL = r"C:\Users\wlane\Documents\Substance_IE_Data\stanford-ner-2015-12-09\lib\*"
    ATTRIB_EXTRACTION_DIR_HOME = r"C:\\Users\\wlane\\Documents\\Substance_IE_Data\\AttributeExtractionModels\\"
else:
    print("Error: unknown user in SystemUtilities/Configuration")

doc_all_gold_dir = gold_annotation_dir + "documents.gold"
doc_dev_gold_dir = gold_annotation_dir + "documents_dev.gold"
doc_test_gold_dir = gold_annotation_dir + "documents_testing.gold"
doc_train_gold_dir = gold_annotation_dir + "documents_training.gold"
patients_all_gold_dir = gold_annotation_dir + "patients.gold"
patients_dev_gold_dir = gold_annotation_dir + "patients_dev.gold"
patients_test_gold_dir = gold_annotation_dir + "patients_testing.gold"
patients_train_gold_dir = gold_annotation_dir + "patients_training.gold"
i2b2_test_gold_dir = gold_annotation_dir + "i2b2\i2b2_test.gold"
i2b2_train_gold_dir = gold_annotation_dir + "i2b2\i2b2_train.gold"
flor_sentence_level_annotations_dir = gold_annotation_dir + "\sentences"
