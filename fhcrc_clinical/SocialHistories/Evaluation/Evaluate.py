from fhcrc_clinical.SocialHistories.Extraction.EventDetection.Processing import *


class EvaluationData:
    def __init__(self):
        self.tp = 0
        self.fn = 0
        self.fp = 0
        self.fn_values = []
        self.fp_values = []

        self.precision = 0
        self.recall = 0
        self.f1 = 0

    def calculate_precision_recall_f1(self):
        if self.tp != 0:
            self.precision = float(self.tp) / float(self.tp + self.fp)
            self.recall = float(self.tp) / float(self.tp + self.fn)

            self.f1 = 2*(self.precision * self.recall)/(self.precision + self.recall)

    def output(self, filename):
        out_file = open(filename, "w")

        out_file.write("Precision: " + str(self.precision) + "\n")
        out_file.write("Recall: " + str(self.recall) + "\n\n")
        out_file.write("F1: " + str(self.f1) + "\n\n")

        out_file.write("<< FN >>\n")
        output_misclassified_elements(self.fn_values, out_file)
        out_file.write("<< FP >>\n")
        output_misclassified_elements(self.fp_values, out_file)


def output_misclassified_elements(elements, out_file):
    """ Output FN or FP elements for error analysis and debugging """
    for element in elements:
        out_file.write("++ " + element.encode("utf8") + "\n")
    out_file.write("\n")
