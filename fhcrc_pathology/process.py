'''author@esilgard'''
#
# Copyright (c) 2014-2016 Fred Hutchinson Cancer Research Center
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

import sys, parser, final_logic
import os, PathClassifier
import global_strings as gb
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
__version__ = 'process_pathology1.0'

####################################################################################
def get_fields(disease_group, report_d, disease_group_data_d, path_data_d):
    '''
    import modules (either general pathology modules, or disease specific depending on parameters)
    disease_group will also serve as the folder that contains all necessary disease specific
    files and modules pathology_d contains parsed path reports in a d of
    {mrn:{acc:{section:{index:text}}}}} data_d maps disease and document relevant
    {field names:[pertinent section(s)]} field_value_d hods values for each of the fields in data_d
    '''

    report_table_d = {}
    error_list = []    
    data_elements = dict.fromkeys(path_data_d.keys() + disease_group_data_d.keys())

    for field in data_elements:
        # import the CLASSES and MODULES for the fields in the disease specific data dictionary
        try:
            if field in disease_group_data_d:
                module = __import__(field, globals(), locals(), [field])                
                if 'Class' in disease_group_data_d.get(field):
                    field_class = getattr(module, field)
                    module = field_class()
            else:
                module = __import__(field, globals(), locals(), [])                
                if 'Class' in path_data_d.get(field):
                    field_class = getattr(module, field)
                    module = field_class()
        except EnvironmentError:
            return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                         'FATAL ERROR could not import ' + field + ' module or class--- \
                         program aborted. ' + str(sys.exc_info()[1])}], Exception)
        try:
            # return fields regardless from module or class
            field_value, return_type = module.get(disease_group, report_d)
        except RuntimeError:
            return ([], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                             'FATAL ERROR could not complete ' + field + ' module or class--- \
                             program aborted. ' + str(sys.exc_info()[1])}], Exception)
        ## organize fields by tables, then individual records, then individual fields
        if return_type == list:
            for each_field in field_value:
                table = each_field.get(gb.TABLE)
                report_table_d[table] = report_table_d.get(table, {})
                report_table_d[table][gb.TABLE] = table
                report_table_d[table][gb.FIELDS] = report_table_d[table].get(gb.FIELDS, [])
                report_table_d[table][gb.FIELDS].append(each_field)
        else:
            error_list += field_value
    report_table_list = report_table_d.values()
    return report_table_list, error_list, list

def get_data_d(disease_group, ml_flag):
    #if disease_group: disease_group = os.path.sep+disease_group
    ''' get disease group data resources '''
    try:
        d = dict((y.split('\t')[0], y.split('\t')[1].strip()) for y in \
            open(PATH + os.path.sep + disease_group + os.path.sep+'data_dictionary.txt', 'r').readlines())
        if ml_flag != 'y':
            d = dict((x,y) for x,y in d.items() if 'ML' not in y)
        return d
    except IOError:
        return {gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR: could not access or parse \
            pathology data dictionary at ' + PATH + os.path.sep + disease_group + 'data_dictionary.txt '}

def main(arguments):
    '''
    current minimum required flags for the pathology parsing in the "arguments" d are:
        -f input pathology file
        -g disease group
    '''
    ml_flag = arguments.get('-ml','n')
    ## get dictionaries/gazeteers needed for processing
    try:
        pathology_d, return_type = parser.parse(arguments.get('-f'))
        if return_type != dict:
            return ([{}], [pathology_d], Exception)
    except IOError:
        return([{}], [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR: could not parse \
                input pathology file ' + arguments.get('-f') + ' --- program aborted'}], Exception)
    disease_group = arguments.get('-g')
    ## general pathology data dictionary ##
    path_data_d = get_data_d('', ml_flag)
    disease_group_data_d = get_data_d(disease_group, ml_flag)
    field_value_output = []
    return_errors = []
    # report counting index (used for timeit tests)
    i = 0
    ## create a list of output field dictionaries ##
    for mrn in pathology_d:
        for accession in pathology_d[mrn]:
            field_value_d = {}
            field_value_d[gb.REPORT] = accession
            field_value_d[gb.MRN] = mrn
            field_value_d[gb.TABLES] = []
            ## write out cannonical version of text and tsv file
            try:
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + accession + '.txt', 'wb') as out_text:
                    out_text.write(pathology_d[mrn][accession][(-1, 'FullText', 0, None)])
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + accession + '.nlp.tsv', 'wb') as out_tsv:
                    specimen_source = pathology_d[mrn][accession].get((0, 'SpecimenSource', 0, None))                   
                    specimen_source_string = '~'.join([')'.join(a) for a in specimen_source.get(0).items()])                    
                    
                    out_tsv.write(gb.MRN_CAPS+'\t'+gb.FILLER_ORDER_NO+'\t'+gb.SET_ID+'\t'+gb.OBSERVATION_VALUE+'\t'+gb.SPECIMEN_SOURCE+'\n')
                    for k,v in pathology_d[mrn][accession].items():
                        if 'SpecimenSource' not in k and 'FullText' not in k and type(v) == dict:
                            for a, b in v.items():
                                try:
                                    out_tsv.write(mrn+'\t'+accession+'\t'+str(a)+'\t'+b+'\t'+specimen_source_string+'\n')
                                #except:
                                #    print a,b
                                #    sys.exit()
                   
            except IOError:
                return (field_value_output, [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                    'FATAL ERROR in pathology/process.py attempting to write text and tsv to files at'+ \
                    arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + accession + \
                    ' - unknown number of reports completed. ' + str(sys.exc_info()[1])}], list)
            ## find disease group in the case of unknown/all --- currently simple keyword/voting
            ## future work to include section specific search and stochastic language model
            if arguments.get('-g') == 'all':
                disease_group, report_info_table = PathClassifier.classify(pathology_d[mrn][accession][(-1, 'FullText', 0, None)])                
                disease_group_data_d = get_data_d(disease_group, ml_flag)
                field_value_d[gb.TABLES].append(report_info_table)
            i += 1
            ## if no Exceptions and "no algorithm" isn't there, then run appropriate algorithms
            if return_type != Exception:
                if arguments.get('-a') == 'n':
                    pass
                else:                    
                    return_fields, return_errors, return_type = get_fields\
                    (disease_group, pathology_d[mrn][accession], disease_group_data_d, path_data_d)
                    field_value_d[gb.TABLES]+=(final_logic.get(return_fields))
                field_value_output.append(field_value_d)

            else:
                
                concatenated_error_string = ';'.join([x[gb.ERR_STR] for x in return_errors])
                return (field_value_output, [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: 'FATAL ERROR \
                        in process.get(fields) -unknown number of reports completed.  \
                        Return error string: ' + concatenated_error_string}], list)
    return (field_value_output, return_errors, list)
