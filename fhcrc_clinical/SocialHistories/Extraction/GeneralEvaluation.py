def calculate_precision_recall_f1(tp, fp, fn):
    precision = None
    recall = None
    f1 = None

    if tp:
        precision = float(tp) / float(tp + fp)
        recall = float(tp) / float(tp + fn)

        f1 = 2*(precision * recall)/(precision+recall)

    return precision, recall, f1
