#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
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

import sys,path_parser,global_strings
import os
path2= os.path.dirname(os.path.realpath(__file__))+'/'
'''author@esilgard'''
'''written October 2014'''
__version__='final_pathology_logic1.0'

def get(table_list):
    '''
    use all the extracted pathology elements from a given report to apply final logic
    add/delete values for the final output
    table_list = list of table dictionaries where
                table dictionary: tableName and a dictionary
                    
    '''   
    return_list=[]   
    for table in table_list:       
        table_d={global_strings.TABLE:table[global_strings.TABLE],global_strings.FIELDS:[]}               
        for each_field in table[global_strings.FIELDS]:
            record_histology_found=False
            specimen_fields=[] 
            if each_field[global_strings.VALUE]:
                if each_field[global_strings.NAME]=='PathFindHistology':
                    record_histology_found=True                    
                table_d[global_strings.FIELDS].append(each_field)
        ## don't report any PathologyFinding values if there was no cancer in the given specimen ##
        if (each_field[global_strings.TABLE]==global_strings.FINDING_TABLE and record_histology_found==False):    
            table_d[global_strings.FIELDS]=[]            
        
        if table_d[global_strings.FIELDS]:            
            return_list.append(table_d)    
    
    return return_list      
