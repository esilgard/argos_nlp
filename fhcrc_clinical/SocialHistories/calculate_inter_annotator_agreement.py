from DataLoading import ServerQuery, IAA


def main():
    # Get filled fields from LabKey
    annotations = ServerQuery.get_annotations_from_server()

    print("Make sure DataLoadingGlobals.JOB_IDS has the interannotated batches for IAA")

    # Reformat data structure for IAA
    iaa_annotations, num_of_annotators = restructure_annotations_for_iaa(annotations)

    # Find inter-annotator agreement
    IAA.calculate_iaa(iaa_annotations, num_of_annotators)


def restructure_annotations_for_iaa(annotations):
    """ Reformat results from server query to match what IAA calculation is expecting"""
    iaa_annotations = {}
    num_of_annotators = len(annotations.keys())

    for annotator in annotations:
        for mrn in annotations[annotator]:
            for doc in annotations[annotator][mrn]:
                add_events(iaa_annotations, doc, annotator, annotations[annotator][mrn][doc])

    return iaa_annotations, num_of_annotators


def add_events(iaa_annotations, doc, annotator, events):
    if doc not in iaa_annotations:
        iaa_annotations[doc] = {}

    iaa_annotations[doc][annotator] = events


if __name__ == '__main__':
    main()
