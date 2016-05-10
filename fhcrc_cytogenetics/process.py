#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
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


import parser, iscn_parser, iscn_string_cleaner
import os, re, sys
import global_strings as gb

'''author@esilgard'''

__version__='process_cytogenetics1.0'

def main(arguments):    
    '''
    current minimum required flags for the pathology parsing in the "arguments" dictionary are:
        -f input cytogenetics file
        -g disease group    
    '''

    try:
        cytogenetics_dictionary, return_type = parser.parse(arguments.get('-f'))        
        if return_type != dict: return ([{}], [cytogenetics_dictionary], Exception)
    except IOError:        
        return([{}], [{gb.ERR_TYPE:'Exception', gb.ERR_STR:'FATAL ERROR: could not parse input cytogenetics file '\
                   +arguments.get('-f') + ' --- program aborted.'}], Exception)

    disease_group = arguments.get('-g')   
    field_value_output = []
    error_output = []
    return_error_list = []

    i = 0
    ## create a list of output field dictionaries ##
    for mrn in cytogenetics_dictionary:
        for acc in cytogenetics_dictionary[mrn]:
            ## write out cannonical version of text and tsv file
            try:
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + acc + '.txt', 'wb') as out_text:
                    out_text.write(cytogenetics_dictionary[mrn][acc][(-1, 'FullText', 0, None)])
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + acc + '.nlp.tsv', 'wb') as out_tsv:
                    specimen_source = cytogenetics_dictionary[mrn][acc].get((0, 'SpecimenSource', 0, None))
                    specimen_source_string = '~'.join([')'.join(a) for a in specimen_source.get(0).items()])                
                    
                    out_tsv.write(gb.MRN_CAPS + '\t' + gb.FILLER_ORDER_NO + '\t' + gb.SET_ID + '\t' + gb.OBSERVATION_VALUE + '\t' + gb.SPECIMEN_SOURCE + '\n')
                    for k,v in cytogenetics_dictionary[mrn][acc].items():
                        if 'SpecimenSource' not in k and 'FullText' not in k and type(v) == dict:
                            for a, b in v.items():
                                out_tsv.write(mrn + '\t' + acc + '\t' + str(a) + '\t' + b + '\t' + specimen_source_string + '\n')                                
                               
            except IOError:
                return (field_value_output, [{gb.ERR_TYPE: 'Exception', gb.ERR_STR: \
                    'FATAL ERROR in cytogenetics/process.py attempting to write text and tsv to files at' + \
                    arguments.get('-f')[:arguments.get('-f').find('.nlp')] + os.path.sep + acc + \
                    ' - unknown number of reports completed. ' + str(sys.exc_info()[1])}], list)


            
            cyto_string = ''
            ## walk through ISCN section in order (by offsets) incase the cytogenetics string is on multiple, sequential lines
            for sections in sorted(cytogenetics_dictionary[mrn][acc], key=lambda x: x[2]):               
                section_header = sections[1]
                beginning_offset = sections[2]                
                if 'ISCN' in section_header:                   
                    karyo_offset = beginning_offset
                    for line, text in sorted(cytogenetics_dictionary[mrn][acc][sections].items(),key=lambda x:x[0]):                        
                        cyto_string += text.strip('"')
            
            if cyto_string:                
                field_value_dictionary = {}
                field_value_dictionary[gb.REPORT] = acc
                field_value_dictionary[gb.MRN] = mrn
                field_value_dictionary[gb.DATE] = (cytogenetics_dictionary[mrn][acc][(-1,'Date',0,None)])
               
                str_cleaner_return_dictionary, karyotype_string = iscn_string_cleaner.get(cyto_string)
                ## if string cleaner does not encounter raw text description of karyotype, then parse string
                if not str_cleaner_return_dictionary:
                    return_fields, return_errors, return_type = iscn_parser.get(karyotype_string, karyo_offset)
                    try:                    
                        exec ('from ' + disease_group + ' import classify_' + disease_group + '_swog_category')
                        exec('cell_list, swog_return_fields, return_errors = classify_' + disease_group + '_swog_category.get\
                            (return_fields, karyotype_string)')
                    except:
                        return (field_value_output, [{gb.ERR_TYPE:'Exception', gb.ERR_STR:\
                                 ' FATAL ERROR in process_cytogenetics.get() - could not retrive disease group specific \
                                cytogenetics module' + str(sys.exc_info())}], list)           

                    try:                
                        with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')] + '/' + acc + '.txt','wb') as out:
                            out.write(cytogenetics_dictionary[mrn][acc][(-1,'FullText',0,None)])
                    except:                                
                        return (field_value_output,[{gb.ERR_TYPE:'Exception', gb.ERR_STR: 'FATAL ERROR in process.py \
                                attempting to write text to file at' + arguments.get('-f')[:arguments.get('-f').find('.nlp')] \
                                + '/' + acc + '.txt - unknown number of reports completed. ' + sys.exc_info()}], list)
                    if return_type != Exception:
                        field_value_dictionary[gb.TABLES] = []
                        field_value_dictionary[gb.TABLES].append({gb.TABLE:'Cytogenetics', gb.FIELDS:swog_return_fields})                    
                        field_value_output.append(field_value_dictionary)
                        if return_errors: return_error_list.append(return_errors)
                    else:
                        return (field_value_output, [{gb.ERR_TYPE:'Exception', gb.ERR_STR:\
                                 ' FATAL ERROR in process_cytogenetics.get() - unknown number of reports completed.' + str(sys.exc_info())}], list)           
                else:
                    field_value_dictionary[gb.TABLES] = []
                    field_value_dictionary[gb.TABLES].append({gb.TABLE:'Cytogenetics', gb.FIELDS:str_cleaner_return_dictionary})                    
                    field_value_output.append(field_value_dictionary)                            
    return field_value_output, return_error_list, list
