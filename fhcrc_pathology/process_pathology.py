#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
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

import sys,path_parser
import os
path2= os.path.dirname(os.path.realpath(__file__))+'/'
'''author@esilgard'''
'''last updated October 2014'''
__version__='process_pathology1.0'

#################################################################################################################################################
def return_exec_code(x):
    '''
        helper method to retrieve the returned field value from each module
    '''
    return x


def get_fields(disease_group,report_dictionary,data_dictionary):
    '''
        disease_group will also serve as the folder that contains all necessary files and modules
        pathology_dictionary contains parsed path reports in a dictionary of {mrn:{acc:{section heading:{index:text}}}}}
        data_dictionary maps disease and document relevant {field names:[pertinent section(s)]}
        field_value_dictionary will hold the values for each of the fields in the data_dictionary
    '''
    report_field_list=[]
    error_list=[]
   
    for field in data_dictionary:
        ## import the modules for the fields in the data dictionary
        
        exec ('from '+disease_group+' import '+field)            
        exec("field_value,return_type=return_exec_code("+field+".get(report_dictionary))")            
        if return_type==dict:
            report_field_list.append(field_value)
        else:
            error_list.append(field_value)
        
    return report_field_list,error_list,list
        
### MAIN CLASS ###
def main(arguments,path):
    '''
    current minimum required flags for the pathology parsing in the "arguments" dictionary are:
        -f input pathology file
        -g disease group
    '''
    
    ## get dictionaries/gazeteers needed for processing
    try:
        pathology_dictionary,return_type=path_parser.parse(arguments.get('-f'))
        if return_type!=dict: return (pathology_dictionary,return_type,Exception)
    except:
        return({'errorType':'Exception','errorString':'FATAL ERROR: could not parse input pathology file '+arguments.get('-f')+' --- program aborted'},Exception,Exception)
  
   
    try:    data_dictionary=dict((y.split('\t')[0],y.split('\t')[1].strip()) for y in open(path2+'/'+arguments.get('-g')+'/data_dictionary.txt','r').readlines())
    except: return ({'errorType':'Exception','errorString':'FATAL ERROR: could not access data dictionary at '+path2+'/'+arguments.get('-g')+'/data_dictionary.txt --- program aborted'},Exception,Exception)

    field_value_output=[]
    
    ## create a list of output field dictionaries ##
    for mrn in pathology_dictionary:            
        for accession in pathology_dictionary[mrn]:
            field_value_dictionary={}
            field_value_dictionary["report"]=accession
            field_value_dictionary["mrn"]=mrn
            #dict.fromkeys(data_dictionary.keys(),None)
            
            return_fields,return_errors,return_type=get_fields(arguments.get('-g'),pathology_dictionary[mrn][accession],data_dictionary)
            
            if return_type!=Exception:
                field_value_dictionary['fields']=return_fields
                field_value_output.append(field_value_dictionary)
            else:
                return (field_value_output,[{'errorType':'Exception','errorString':'FATAL ERROR in process_pathology.get(fields) unknown number of fields completed'}],list)
    #field_value_dictionary,return_type=get_fields(arguments.get('-g'),pathology_dictionary,data_dictionary,field_value_dictionary)
    return (field_value_output,return_errors,list)
