from fhcrc_clinical.SocialHistories.SystemUtilities import Configuration
import os

def print_status_classification_results(sentences, classifications, event_type):
    with open(os.path.join(Configuration.DATA_DIR, "status_classification_"+event_type+ "_debug.txt"), "wb") as file:
        for i in range(0, len(sentences)-1, 1):
            sent = sentences[i]
            predicted_class = classifications[i]
            text = sent.text
            file.write(predicted_class.encode("utf8") + ": \n\t" + text + "\n")

