'''author@esilgard'''
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

import global_strings
__version__ = 'final_pathology_logic1.0'

def get(table_list):
    '''
    use all the extracted pathology elements from a given report to apply final logic
    add/delete values for the final output
    table_list = list of table dictionaries where
                table dictionary: tableName and a dictionary
    '''
    return_list = []
    ## iterate through the tables
    for table in table_list:
        field_list = []
        ## iterate through PathFinding values, find the specimen (recordKey) PathFindingHistology
        if table[global_strings.TABLE] == global_strings.FINDING_TABLE:
            specimen_histology_found = set([])
            for fields in table[global_strings.FIELDS]:
                if fields[global_strings.NAME] == "PathFindHistology" \
                   and fields[global_strings.VALUE]:
                    specimen_histology_found.add(fields[global_strings.KEY])
            ## iterate through fields again, only ones that have histologies to the final list
            for fields in table[global_strings.FIELDS]:
                if fields[global_strings.KEY] in specimen_histology_found:
                    field_list.append(fields)
        else:
            for fields in table[global_strings.FIELDS]:
                if fields[global_strings.VALUE]:
                    field_list.append(fields)
        if field_list:
            table[global_strings.FIELDS] = field_list
            return_list.append(table)
    return return_list
