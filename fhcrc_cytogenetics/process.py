'''author@esilgard'''
#
# Copyright (c) 2015-2016 Fred Hutchinson Cancer Research Center
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

import parser
import iscn_parser
import iscn_string_cleaner
import os
import re
import sys
import global_strings as gb
__version__ = 'process_cytogenetics1.0'
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

################################################################################
def get_fields(disease_group, disease_group_data_d, return_fields, karyotype_string, karyo_offset):
    '''
    import modules (either general cytogenetics, or disease specific depending on parameters)
    disease_group will also serve as the folder that contains all necessary disease specific
    files and modules cytogenetics_d contains parsed path reports in a dict of
    {mrn:{acc:{section:{index:text}}}}} data_d maps disease and document relevant
    {field names:[pertinent section(s)]} field_value_d holds values for each of the fields
    '''
    report_table_list = []
    error_list = []
    data_elements = dict.fromkeys(disease_group_data_d.keys())

    for field in data_elements:
        # import the CLASSES and MODULES for the fields in the disease specific data dictionary
        try:
            if field in disease_group_data_d:
                module = __import__(disease_group + '.' + field, globals(), locals(), [field])
                if 'Class' in disease_group_data_d.get(field):
                    field_class = getattr(module, field)
                    module = field_class()

        except EnvironmentError:
            return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                         'FATAL ERROR could not import ' + field + ' module or class--- \
                         program aborted. ' + str(sys.exc_info()[1])}], Exception)
        try:
            # return fields regardless from module or class
            field_value, return_type = module.get(return_fields, karyotype_string, karyo_offset)
        except RuntimeError:
            return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                             'FATAL ERROR could not complete ' + field + ' module or class--- \
                             program aborted. ' + str(sys.exc_info(0)[1])}], Exception)

        ##  organize fields by tables, records, then fields
        if isinstance(return_type, list):
            report_table_list += field_value
        else:
            error_list += field_value

    #report_table_list = report_table_d.values()
    return report_table_list, error_list, list


def get_data_d(disease_group, ml_flag):
    ''' get disease group data resources '''
    try:
        d = dict((y.split('\t')[0], y.split('\t')[1].strip()) for y in \
            open(PATH + disease_group + os.path.sep+'data_dictionary.txt', 'r').readlines())
        if ml_flag != 'y':
            data_d = dict((x, y) for x, y in d.items() if 'ML' not in y)
        return data_d
    except IOError:
        return Exception


def main(arguments):
    '''
    current minimum required flags for the pathology parsing in the "arguments" dictionary are:
        -f input cytogenetics file
        -g disease group
    '''
    ml_flag = arguments.get('-ml', 'n')
    try:
        cytogenetics_d, return_type = parser.parse(arguments.get('-f'))
        if return_type != dict:
            return ([{}], [cytogenetics_d], Exception)
    except IOError:
        return([{}], [{gb.ERR_TYPE:'Exception', gb.ERR_STR:'FATAL ERROR: could not parse input \
        cytogenetics file ' + arguments.get('-f') + ', program aborted.'}], Exception)

    disease_group = arguments.get('-g')
    ## temporary error message attempting to classify in cytogenetics branch
    if disease_group == 'all':
        return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR in process; \
        cytogenetics branch does not classify reports by disease group,\
        "all" is not an acceptable disease group input for this report type'}], list)

    ## disease specific cytogenetics data dictionary (no general algorithms currently)
    disease_group_data_d = get_data_d(disease_group, ml_flag)
    if disease_group_data_d == Exception:
        return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR: could not access  \
            or parse data dictionary at ' + PATH + os.path.sep + disease_group + os.path.sep + \
            'data_dictionary.txt verify that "' + disease_group + '" is a valid disease group \
            for this report type'}], Exception)
    field_value_output = []
    return_error_list = []

    # report counting index (used for timeit tests)
    i = 0
    ## create a list of output field dictionaries ##
    for mrn in cytogenetics_d:
        for acc in cytogenetics_d[mrn]:
            ## write out cannonical version of text and tsv file
            try:
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + \
                os.path.sep + acc + '.txt', 'wb') as out_text:
                    out_text.write(cytogenetics_d[mrn][acc][(-1, 'FullText', 0, None)])
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + \
                os.path.sep + acc + '.nlp.tsv', 'wb') as out_tsv:
                    specimen_source = cytogenetics_d[mrn][acc].get((0, 'SpecimenSource', 0, None))
                    specimen_source_string = '~'.join([')'.join(a) for a in \
                    specimen_source.get(0).items()])

                    out_tsv.write(gb.MRN_CAPS + '\t' + gb.FILLER_ORDER_NO + '\t' + gb.SET_ID + \
                    '\t' + gb.OBSERVATION_VALUE + '\t' + gb.SPECIMEN_SOURCE + '\n')
                    for k,v in cytogenetics_d[mrn][acc].items():
                        if 'SpecimenSource' not in k and 'FullText' not in k and isinstance(v, dict):
                            for a, b in v.items():
                                out_tsv.write(mrn + '\t' + acc + '\t' + str(a) + '\t' + b + \
                                '\t' + specimen_source_string + '\n')

            except IOError:
                return (field_value_output, [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                    'FATAL ERROR in process.py attempting to write text and tsv to files at' + \
                    arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + acc + \
                    ' - unknown number of reports completed. ' + str(sys.exc_info()[1])}], list)


            ## placeholder for a disease group classification in the case of unknown/all
            ## this doesn't exist yet for cytology reports - and it's unclear if it's needed

            i += 1
            cyto_string = ''
            ## if "no algorithm" isn't there, then run appropriate algorithms
            if arguments.get('-a') == 'n':
                pass
            else:
                ## walk through ISCN section in order in case the karyotype on multiple lines
                ## this means all cytogenetics algorithms will only be based on ISCN string
                for sections in sorted(cytogenetics_d[mrn][acc], key=lambda x: x[2]):
                    section_header = sections[1]
                    beginning_offset = sections[2]
                    if 'ISCN' in section_header:
                        karyo_offset = beginning_offset
                        for line, text in sorted(cytogenetics_d[mrn][acc][sections].items(), \
                        key=lambda x: x[0]):
                            cyto_string += text

                if cyto_string:
                    field_value_dictionary = {}
                    field_value_dictionary[gb.REPORT] = acc
                    field_value_dictionary[gb.MRN] = mrn                   

                    str_cleaner_return_dictionary, karyotype_string, karyo_offset = \
                    iscn_string_cleaner.get(cyto_string, karyo_offset)
                    ## if string cleaner doesn't find description of karyotype, then parse string
                    if not str_cleaner_return_dictionary:
                        return_fields, return_errors, return_type = iscn_parser.get\
                       (karyotype_string, karyo_offset)
                        try:
                            
                            return_fields, return_errors, return_type = get_fields\
                            (disease_group, disease_group_data_d, return_fields, \
                            karyotype_string, karyo_offset)
                           
                            #field_value_output.append(field_value_dictionary)
                        except IOError:
                            return (field_value_output, [{gb.ERR_TYPE:'Exception', gb.ERR_STR:\
                            'FATAL ERROR in process.get() - \
                            could not retrieve disease group specific module' + \
                            str(sys.exc_info(1))}], list)
                        if return_type != Exception:
                            field_value_dictionary[gb.TABLES] = [{gb.TABLE:gb.CYTOGENETICS, gb.FIELDS:return_fields}]
                            field_value_output.append(field_value_dictionary)
                            if return_errors:
                                return_error_list.append(return_errors)
                        else:
                            concatenated_error_string = ';'.join([x[gb.ERR_STR] for x in return_errors])

                            return (field_value_output, [{gb.ERR_TYPE:'Exception', gb.ERR_STR:\
                            'FATAL ERROR in process.get(). Unknown number of reports completed.' + \
                            str(sys.exc_info(1))}], list)
                    else:                        
                        ## string cleaner extracted a text based classification
                        field_value_dictionary[gb.TABLES] = []                        
                        field_value_dictionary[gb.TABLES].append({gb.TABLE:gb.CYTOGENETICS, \
                        gb.FIELDS:str_cleaner_return_dictionary})
                        field_value_output.append(field_value_dictionary)

    return (field_value_output, return_error_list, list)
