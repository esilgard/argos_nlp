'''author@esilgard'''
#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys, parser
import os, csv
import global_strings as gb
from SocialHistories import extract_substance_info
from SocialHistories.Preprocessing.generate_notes import load_caisis_silver_annotations

PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
__version__ = 'process_clinical1.0'


####################################################################################
def get_fields(report_d, clinical_data_d, mrn, accession, patient_substance_info, mrn_caisis_map):
    """
    import modules, reprt_d contains parsed notes in a dict of
    {patient id:{report id:{section:{index:text}}}}} 
    clinical_data_d is a dict of values for each of the fields in data_d
    """
    report_table_d = {}
    error_list = []
    data_elements = dict.fromkeys(clinical_data_d.keys())

    for field in data_elements:
        # import the CLASSES and MODULES for the fields in the data dictionary
        module = import_classes_and_modules(field, clinical_data_d)

        # get field values
        field_value, return_type = get_field_values(module, report_d, field, mrn, accession, patient_substance_info,
                                                    mrn_caisis_map)


        # organize fields by tables, then individual records, then individual fields
        if return_type == list:
            for each_field in field_value:
                # catch and release fields with NULL/None value ToDo: Make this into a downstream filter of some kind?
                if each_field['Value'] != None:
                    table = each_field.get(gb.TABLE)
                    report_table_d[table] = report_table_d.get(table, {})
                    report_table_d[table][gb.TABLE] = table
                    report_table_d[table][gb.FIELDS] = report_table_d[table].get(gb.FIELDS, [])
                    report_table_d[table][gb.FIELDS].append(each_field)
        else:
            error_list += field_value

    report_table_list = report_table_d.values()
    return report_table_list, error_list, list


def get_data_d():
    """ get resources """
    d = dict((y.split()[0], y.split()[1].strip()) for y in \
             open(PATH + os.path.sep + 'data_dictionary.txt', 'r').readlines())
    return d


def main(arguments):
    """
    current minimum required flags for the clinical parsing in the "arguments" d are:
    -f input pathology file
    """
    # get dictionaries/gazeteers needed for processing
    clinical_d, return_type, clinical_data_d = get_clinical_dicts(arguments)
    field_value_output = []
    return_errors = []

    # Extract substance information
    patient_substance_info = extract_substance_info.main("execute", arguments['-f'])
    print "Finished extracting substance info"

    # create a list of output field dictionaries
    mrn_caisis_map, dict2 = load_caisis_silver_annotations()
    create_output_field_dicts(arguments, clinical_d, return_type, clinical_data_d, field_value_output, return_errors,
                              patient_substance_info, mrn_caisis_map)

    return field_value_output, return_errors, list


def get_clinical_dicts(arguments):
    try:
        clinical_d, return_type = parser.parse(arguments.get('-f'))
        if return_type != dict:
            return [{}], [clinical_d], Exception
    except IOError:
        return ([{}], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR: error in clinical note parser with input ' \
                                                              + arguments.get('-f') + ' --- program aborted'}],
                Exception)

    # general clinical data dictionary
    clinical_data_d = get_data_d()
    return clinical_d, return_type, clinical_data_d


def create_output_field_dicts(arguments, clinical_d, return_type, clinical_data_d, field_value_output, return_errors,
                              patient_substance_info, mrn_caisis_map):
    for mrn in clinical_d:
        for accession in clinical_d[mrn]:
            field_value_d = dict()
            field_value_d[gb.REPORT] = accession
            field_value_d[gb.MRN] = mrn
            field_value_d[gb.TABLES] = []

            # write out canonical version of text file
            try:
                folder = arguments.get('-f')[:arguments.get('-f').find('.nlp')]
                full_text = clinical_d[mrn][accession][(-1, 'FullText', 0)]
                date = clinical_d[mrn][accession][(-2, gb.EVENT_DATE, 0)]
                with open(folder + os.path.sep + accession + '.txt', 'wb') as out_text:
                    out_text.write(full_text)
                with open(folder + os.path.sep + accession + '.nlp.tsv', 'wb') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',')
                    csv_writer.writerow([gb.MRN_CAPS, gb.FILLER_ORDER_NO, gb.EVENT_DATE, gb.OBSERVATION_VALUE])
                    csv_writer.writerow([mrn, accession, date, full_text])

            except IOError:
                return (field_value_output, [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                    'FATAL ERROR in clinical/process.py attempting to write text and tsv to files at' + \
                    folder + os.path.sep + accession + '.txt' \
                                                       ' - unknown number of reports completed. ' + str(
                        sys.exc_info()[1])}], list)

            # if no Exceptions and "no algorithm" isn't there, then run appropriate algorithms
            if return_type != Exception:
                if arguments.get('-a') == 'n':
                    pass
                else:
                    return_fields, return_errors, return_type = get_fields(clinical_d[mrn][accession], clinical_data_d,
                                                                           mrn, accession, patient_substance_info,
                                                                           mrn_caisis_map)
                    field_value_d[gb.TABLES] += return_fields
                field_value_output.append(field_value_d)
            else:
                concatenated_error_string = ';'.join([x[gb.ERR_STR] for x in return_errors])
                return (field_value_output, [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR \
                    in process.get(fields) -unknown number of reports completed.  \
                    Return error string: ' + concatenated_error_string}], list)


def import_classes_and_modules(field, clinical_data_d):
    try:
        module = __import__(field, globals(), locals(), [])
        if 'Class' in clinical_data_d.get(field):
            field_class = getattr(module, field)
            module = field_class()
    except EnvironmentError:
        return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
            'FATAL ERROR could not import ' + field + ' module or class--- \
            program aborted. ' + str(sys.exc_info()[1])}], Exception)

    return module


def get_field_values(module, report_d, field, mrn, accession, patient_substance_info, mrn_caisis_map):
    try:
        # return fields regardless from module or class
        field_value, return_type = module.get(report_d, field, mrn, accession, patient_substance_info, mrn_caisis_map)
    except RuntimeError:
        return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
            'FATAL ERROR could not complete ' + field + ' module or class--- \
            program aborted. ' + str(sys.exc_info()[1])}], Exception)

    return field_value, return_type
