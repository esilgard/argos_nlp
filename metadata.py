''' author@esilgard '''
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
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

import sys, json

def get(nlp_engine_path, arguments):
    '''
        read in full json metadata dictionary from resource file
        return metadata dictionary of relavent fields for the given
        document and disease group
    '''
    ## path to file containing the metadata dictionary (in json format) ##
    try:
        meta_data_file = open(nlp_engine_path + 'metadata.json', 'r')
        try:
            metadata_d = json.load(meta_data_file)
            meta_data_file.close()
        except Exception:
            sys.stderr.write('FATAL ERROR: json could not load metadata dictionary file, \
                            potential formatting error.  program aborted.')
            sys.exit(1)
    except Exception:
        sys.stderr.write('FATAL ERROR: metadata dictionary not found.  program aborted.')
        sys.exit(1)
    return_metadata_d = {}
    ## only return list of relevant tables
    return_table_list = []
    ## only output the appropriate metadata for the given document type and disease group
    for table_dictionary in metadata_d.get(arguments.get('-t'))['tables']:
        ## table_dictionary has two keys - "table":table_name and
        ## "fields": [multiple_field_dictionaries]
        return_field_list = []
        for field_dictionary in table_dictionary['fields']:
            ## only return relevant fields in that table
            return_field_dictionary = {}
            return_disease_properties_list = []
            for disease_group_dictionary in field_dictionary.get("diseaseProperties"):
                ## only return relevant values for that disease group  (or general '*'
                ## patients/all disease groups)
                if arguments.get('-g') in disease_group_dictionary.get("diseaseGroup") or \
                   '*' in disease_group_dictionary.get("diseaseGroup"):
                    return_disease_properties_list.append(disease_group_dictionary)
            if return_disease_properties_list:
                return_field_dictionary = field_dictionary
                return_field_dictionary["diseaseProperties"] = return_disease_properties_list
            if return_field_dictionary:
                return_field_list.append(return_field_dictionary)
        if return_field_list:
            return_table_dictionary = {'fields': return_field_list, \
                                       'table': table_dictionary['table']}
            return_table_list.append(return_table_dictionary)
    if return_table_list:
        return_metadata_d['tables'] = return_table_list

    return return_metadata_d
