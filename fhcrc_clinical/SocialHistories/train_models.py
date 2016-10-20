# train classifiers and extractors and output models
import DataLoading.DataLoader
from Extraction.EventDetection import Training as EventDetectionTraining
from Extraction.StatusClassification import Training as StatusClassificationTraining
from Extraction.EventAttributeLinking import Training as EventFillerTraining
from Extraction.AttributeExtraction import Training as AttributeExtractionTraining
from Extraction.AttributeExtraction import Training_CRFSuite
from SystemUtilities import Shelver


def main():
    # Set which division of data to use
    DATA_SPLIT = "Train"

    # Load Data
    patients = DataLoading.DataLoader.main(DATA_SPLIT)  # list of filled Patient objects

    # Event Detection
    EventDetectionTraining.train_event_detectors(patients)

    # Status classification
    StatusClassificationTraining.train_status_classifier(patients)

    #Shelver.shelve_patients(patients)
    #patients = Shelver.unshelve_patients()

    # Attribute Extraction
    Training_CRFSuite.train(patients)

    # Event Filling
    EventFillerTraining.train_event_fillers(patients)


if __name__ == '__main__':
    main()
