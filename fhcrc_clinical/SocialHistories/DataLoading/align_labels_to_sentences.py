import os


def main():
    sent_dir = r'C:\Users\sdmorris\Documents\FHCRC\Resources\Florian\Florian_smoking\smoking_status\SmokingStatusAnnotator\resources\gold\sentences'
    data_dir = r''
    sent_labels = {}

    # Grab labeled data from every gold file in directory
    for subdir, dirs, files in os.walk(sent_dir):
        for filename in files:
            filepath = sent_dir + "\\" + filename
            with open(filepath, "r") as gold_file:
                gold_lines = gold_file.readlines()

            add_labels(gold_lines, sent_labels)

    print(sent_labels)

    # Grab docs and match up labels
    '''
    for subdir, dirs, files in os.walk(data_dir):
        for filename in files:
            filepath = sent_dir + "\\" + filename
            with open(filepath, "r") as doc_file:
                doc_lines = doc_file.readlines()

            match_sentences(doc_lines, sent_labels, filename)
    '''


def add_labels(gold_lines, sent_labels):
    for line in gold_lines:
        chunks = line.split()

        # The first gram is the label, the rest is the sentence
        if len(chunks) > 1:
            label = chunks[0]
            sentence = line.lstrip(label)
            sentence = sentence.strip("     \n")    # space, tab, newline
            label = label.upper()

            if sentence not in sent_labels:
                sent_labels[sentence] = label

            # If there's a conflicting sentence label print error message
            elif label != sent_labels[sentence]:
                print("Duplicate sentence with different label!!\n" + sentence +
                      "\n" + label + " " + sent_labels[sentence])


def match_sentences(doc_lines, sent_labels, filename):
    pass


if __name__ == '__main__':
    main()
