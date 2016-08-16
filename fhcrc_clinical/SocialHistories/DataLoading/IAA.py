import csv
from SystemUtilities.Globals import *
from SystemUtilities.Configuration import IAA_DISAGREEMENT_LOG, IAA_OUT_FILE, SPAN_DISAGREEMENT_LOG


class FieldIAAInfo:
    """ Matrix information for Fleiss Kappa calculation """
    def __init__(self, rows, column_sums, occurrences=0):
        self.rows = rows
        self.column_sums = column_sums
        self.total = sum(column_sums)
        self.occurrences = occurrences


def calculate_iaa(annotations, num_of_annotators):
    """Use Fleiss Kappa for several annotator interrater agreement"""
    value_infos, highlight_infos = field_iaa_info(annotations)

    # kappa for each individual field
    output_iaa(value_infos, highlight_infos, num_of_annotators)


def field_iaa_info(annotations):
    """ Find Fleiss kappa matrix info for each field """
    value_field_infos = {subst: {} for subst in SUBSTANCE_TYPES}
    highlight_field_infos = {subst: {} for subst in SUBSTANCE_TYPES}

    value_disagreements = {}
    span_disagreements = {}

    # Find matrix info and disagreements for each field
    for substance in SUBSTANCE_TYPES:
        for field in FIELDS:
            # value IAA
            value_field_infos[substance][field] = get_single_field_info(annotations, substance, field,
                                                                        value_disagreements)

            # highlighted regions IAA
            highlight_field_infos[substance][field] = \
                get_single_field_info(annotations, substance, field, span_disagreements, spans_instead_of_value=True)

    log_disagreements(value_disagreements, span_disagreements)

    return value_field_infos, highlight_field_infos


def get_single_field_info(annotations, substance, field, disagreements, spans_instead_of_value=False):
    if spans_instead_of_value:
        field = get_single_field_spans_info(annotations, substance, field, disagreements)
    else:
        field = get_single_field_value_info(annotations, substance, field, disagreements)

    return field


def get_single_field_value_info(annotations, substance, field, disagreements):
    """ Track matrix of inter-annotated values for a field for all documents """
    column_value_map = {}   # {value: column number}
    map_decoder = []        # [value]
    column_map_index = 0
    column_sums = []
    rows = []

    occurrences = 0

    for doc_id in annotations:
        row = [0 for _ in column_value_map]

        for annotator in annotations[doc_id]:
            event = annotations[doc_id][annotator][substance]
            value = get_field_value(event, field)

            # Keep track of non-blank values
            if value:
                occurrences += 1

            # update rows and columns
            if value not in column_value_map:
                row.append(1)
                column_sums.append(1)
                column_value_map[value] = column_map_index
                map_decoder.append(value)
                column_map_index += 1
            else:
                column = column_value_map[value]
                row[column] += 1
                column_sums[column] += 1

        rows.append(row)
        field_disagreements_per_doc(disagreements, row, map_decoder, substance, field, doc_id)

    return FieldIAAInfo(rows, column_sums, occurrences)


def get_single_field_spans_info(annotations, substance, field, log_file):
    """ Track matrix of inter-annotated spans for a field for all documents """
    # Track matrix of annotated values
    column_value_map = []  # [value] -- can't do dict bc lists of spans aren't hashable
    column_map_index = 0
    column_sums = []
    rows = []

    disagreements = []
    occurrences = 0

    for doc_id in annotations:
        row = [0 for _ in column_value_map]

        for annotator in annotations[doc_id]:
            event = annotations[doc_id][annotator][substance]
            value = get_field_spans(event, field)

            # Keep track of non-blank values
            if value:
                occurrences += 1

            # Check if the value given is new or a duplicate
            value_in_map, column = check_if_exact_spans_in_map(column_value_map, value)

            # update rows and columns
            if not value_in_map:
                row.append(1)
                column_sums.append(1)
                column_value_map.append(value)
                column_map_index += 1
            else:
                row[column] += 1
                column_sums[column] += 1

        rows.append(row)
        disagreements.append(field_disagreements_per_doc(log_file, row, column_value_map, substance, field, doc_id))

    return FieldIAAInfo(rows, column_sums, occurrences)


def check_if_exact_spans_in_map(seen_span_lists, span_list):
    previously_seen = False
    column_index = 0

    for column_index, seen_span_list in enumerate(seen_span_lists):
        total_match = spans_totally_match(seen_span_list, span_list)
        if total_match:
            previously_seen = True
            break

    return previously_seen, column_index


def spans_totally_match(seen_span_list, span_list):
    total_match = True

    if len(seen_span_list) != len(span_list):
        total_match = False
    else:
        for seen_span, span in zip(seen_span_list, span_list):
            if seen_span.start != span.start or seen_span.stop != span.stop:
                total_match = False
                break

    return total_match


def get_field_value(event, field):
    value = ""
    if field == STATUS:
        value = event.status
    elif field in event.attributes:
        value = event.attributes[field].text
    return value


def get_field_spans(event, field):
    value = ""
    if field == STATUS:
        value = event.status_spans
    elif field in event.attributes:
        value = event.attributes[field].spans
    return value


def find_iaa(list_of_field_infos, num_of_annotators):
    """ Fleiss kappa calculation using each field's matrix info in FieldIAAInfo objects """
    combined_info = combine_different_value_field_infos(list_of_field_infos)

    if combined_info.occurrences > 0:
        kappa = calculate_fleiss_kappa(combined_info, num_of_annotators)
    else:
        kappa = None

    return kappa


def combine_different_value_field_infos(list_of_field_infos):
    """ Simply append rows and columns together """
    rows = []
    column_sums = []
    occurrences = 0
    if list_of_field_infos:
        for field_index, field_info in enumerate(list_of_field_infos):
            rows.extend(field_info.rows)
            column_sums.extend(field_info.column_sums)
            occurrences += field_info.occurrences

    return FieldIAAInfo(rows, column_sums, occurrences)


def combine_same_value_field_infos(list_of_field_infos):
    """ append rows and sum columns together """
    rows = []
    column_sums = []
    occurrences = 0
    if list_of_field_infos:

        # Set column_sum to the column_sums of the first field
        column_sums = list_of_field_infos[0].column_sums
        for field_index, field_info in enumerate(list_of_field_infos):
            # Grab each row
            rows.extend(field_info.rows)
            occurrences += field_info.occurrences

            # Add all non-first column sums to the first one
            if field_index > 0:
                for column_index, column_sum in enumerate(field_info.column_sums):
                    column_sums[column_index] += column_sum

    return FieldIAAInfo(rows, column_sums, occurrences)


def calculate_fleiss_kappa(combined_info, num_of_annotators):
    # Find Pj for calculating Pe
    pj = [float(c) / float(combined_info.total) for c in combined_info.column_sums]
    expected_prob = sum([c ** 2 for c in pj])

    # Find Pi for calculating P
    pi = []
    for row in combined_info.rows:
        pi_coefficient = float(1) / float(num_of_annotators * (num_of_annotators - 1))
        pi_sum = sum([v ** 2 for v in row]) - num_of_annotators
        pi.append(pi_coefficient * pi_sum)

    observed_prob = float(sum(pi)) / float(len(pi))

    # Use P and Pe to calculate kappa
    if expected_prob != 1:
        kappa = float((observed_prob - expected_prob)) / float((1 - expected_prob))
    else:
        kappa = 1

    return kappa


def field_disagreements_per_doc(disagreements, row, column_value_map, substance, field, doc_id):
    """ Track the disagreements found for a specific field for each doc """
    if len(row) > 1:
        # Find values used by any annotator
        values = []
        for column_index, count in enumerate(row):
            if count != 0:
                values.append(column_value_map[column_index])

        # If there are more than one, track them as disagreements
        if len(values) > 1:
            if doc_id not in disagreements:
                disagreements[doc_id] = {substance: {} for substance in SUBSTANCE_TYPES}
            if field not in disagreements[doc_id][substance]:
                disagreements[doc_id][substance][field] = values


def log_disagreements(value_disagreements, span_disagreements):
    """ Output disagreements to a log file """
    # Get field value and span disagreements
    docs_with_disagreements = set(value_disagreements.keys()) | set(span_disagreements.keys())

    # Set up file output
    tsv_file = open(IAA_DISAGREEMENT_LOG, "wb")
    tsv_writer = csv.writer(tsv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
    # span_tsv_file = open(SPAN_DISAGREEMENT_LOG, "wb")
    # span_tsv_writer = csv.writer(span_tsv_file, delimiter='\t', quoting=csv.QUOTE_ALL)

    # Write disagreements to file
    for doc_id in docs_with_disagreements:
        # Field value disagreements
        if doc_id in value_disagreements:
            write_disagreements_to_tsv_file(value_disagreements, doc_id, tsv_writer)

        # Field highlighted span disagreements
        # if doc_id in span_disagreements:
            # write_disagreements_to_tsv_file(value_disagreements, doc_id, span_tsv_writer, values_are_spans=True)


def write_disagreements_to_text_file(disagreements, doc_id, log_file, values_are_spans=False):
    for substance in disagreements[doc_id]:
        for field in disagreements[doc_id][substance]:
            values = get_disagreeing_values(disagreements[doc_id][substance][field], values_are_spans)
            log_file.write(substance + field + ":\n\t\t")
            log_file.write(str(values) + "\n\t")


def write_disagreements_to_tsv_file(disagreements, doc_id, tsv_writer, values_are_spans=False):
    for substance in disagreements[doc_id]:
        for field in disagreements[doc_id][substance]:
            values = disagreements[doc_id][substance][field]
            # values =  get_disagreeing_values(disagreements[doc_id][substance][field], values_are_spans)
            write_tsv_line(values, tsv_writer, doc_id, substance, field)


def write_tsv_line(values, tsv_writer, doc_id, substance, field):
    row = [doc_id, substance + field]
    row.extend(values)
    tsv_writer.writerow(row)


def get_disagreeing_values(values, values_are_spans):
    """ Get values in a format that will work for printing to a file
    Used if printing both """
    values_for_printing = []

    if not values_are_spans:
        # If not spans then no need to convert
        values_for_printing = values
    else:
        # Convert Span object lists to tuples for printing
        for span_list in values:

            spans_for_printing = []
            for span in span_list:
                span_for_printing = (span.start, span.stop)
                spans_for_printing.append(span_for_printing)

            values_for_printing.append(spans_for_printing)

    return values_for_printing


def output_iaa(value_infos, highlight_infos, num_of_annotators):
    iaa_file = open(IAA_OUT_FILE, "w")

    for subst in SUBSTANCE_TYPES:
        iaa_file.write("\n" + subst + "\n")
        fields = [STATUS] + ATTRIBS[subst]
        for field in fields:
            value_kappa = find_iaa([value_infos[subst][field]], num_of_annotators)
            span_kappa = find_iaa([highlight_infos[subst][field]], num_of_annotators)
            iaa_file.write(field + "\n\tvalue: " + str(value_kappa) + "\n")
            iaa_file.write("\tspans: " + str(span_kappa) + "\n")
