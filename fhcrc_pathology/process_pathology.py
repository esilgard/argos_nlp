# -*- coding: utf-8 -*-
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

import sys,path_parser,final_logic,re
import os,global_strings,PathClassifier
path2= os.path.dirname(os.path.realpath(__file__))+'/'
'''author@esilgard'''
__version__='process_pathology1.0'

#################################################################################################################################################
def return_exec_code(x):
    '''
        helper method to retrieve the returned field value from each module
    '''
    return x


def get_fields(disease_group,report_dictionary,disease_group_data_dictionary,path_data_dictionary):
    
    '''
        import modules (either general pathology modules, or disease specific depending on parameters)
        disease_group will also serve as the folder that contains all necessary disease specific files and modules
        pathology_dictionary contains parsed path reports in a dictionary of {mrn:{acc:{section:{index:text}}}}}
        data_dictionary maps disease and document relevant {field names:[pertinent section(s)]}
        field_value_dictionary will hold the values for each of the fields in the data_dictionary
    '''
   
    report_table_d={}
    error_list=[]
    data_elements=dict.fromkeys(path_data_dictionary.keys()+disease_group_data_dictionary.keys())
    for field in data_elements:
        ## import the CLASSES and MODULES for the fields in the disease specific data dictionary, back off to general if there is no disease specific version ##
        if field in disease_group_data_dictionary:
            try:
                exec ('from '+disease_group+' import '+field)                
                if disease_group_data_dictionary.get(field)=='Class':                                   
                    exec("fieldClass=return_exec_code("+field+"."+field+"())")
                    field_value,return_type=fieldClass.get(disease_group,report_dictionary)                    
               ## module import (note there's no final else, which means "SecondaryClass" types do not get called here (imported above)
                elif disease_group_data_dictionary.get(field)=='Module':                 
                    exec("field_value,return_type=return_exec_code("+field+".get(disease_group,report_dictionary))")
                    
            except:                
                return ({},{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR could not import disease specific '+field+' module or class --- program aborted. '+str(sys.exc_info()[1])},Exception)
        else:           
            try:
                exec('import '+field)
                if path_data_dictionary.get(field)=='Class':                   
                    exec("fieldClass=return_exec_code("+field+"."+field+"())")                   
                    field_value,return_type=fieldClass.get(disease_group,report_dictionary)
                    
                ## module import (note there's no final else, which means "SecondaryClass" types do not get called here (imported above)
                elif disease_group_data_dictionary.get(field)=='Module':  
                    exec("field_value,return_type=return_exec_code("+field+".get(disease_group,report_dictionary))")
                   
            except:
                return ({},{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR could not complete '+field+' module or class--- program aborted. '+str(sys.exc_info()[1])},Exception)
            
        ## organize fields by tables, then individual records, then individual fields
        
        if return_type==list:
            
            for each_field in field_value:                
                table=each_field.get(global_strings.TABLE)
                report_table_d[table]=report_table_d.get(table,{})
                report_table_d[table][global_strings.TABLE]=table
                report_table_d[table][global_strings.FIELDS]= report_table_d[table].get(global_strings.FIELDS,[])
                report_table_d[table][global_strings.FIELDS].append(each_field)
            
        else:
            error_list+=field_value
    report_table_list=report_table_d.values()    
    return report_table_list,error_list,list

def get_disease_specific_dictionary(disease_group):
    ## disease group data dictionary ##
    try:
         return dict((y.split('\t')[0],y.split('\t')[1].strip()) for y in open(path2+'/'+disease_group+'/data_dictionary.txt','r').readlines())
    except:
        return {global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not access or parse disease specific pathology data dictionary at '+path2+'/'+disease_group+'/data_dictionary.txt '}

        
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
        if return_type!=dict: return ({},pathology_dictionary,Exception)
    except:
        return({},{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not parse input pathology file '+arguments.get('-f')+' --- program aborted'},Exception)
    disease_group=arguments.get('-g')
    
    ## general pathology data dictionary ##
    try:    path_data_dictionary=dict((y.split('\t')[0],y.split('\t')[1].strip()) for y in open(path2+'/data_dictionary.txt','r').readlines())
    except: return ({},{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not access or parse pathology data dictionary at '+path2+'/data_dictionary.txt --- program aborted'},Exception)
   
    disease_group_data_dictionary = get_disease_specific_dictionary(disease_group)
    field_value_output=[]
    error_output=[]
    i=0
    ## create a list of output field dictionaries ##
    for mrn in pathology_dictionary:            
        for accession in pathology_dictionary[mrn]:
            field_value_dictionary={}
            field_value_dictionary[global_strings.REPORT]=accession
            field_value_dictionary[global_strings.MRN]=mrn
            ## write out cannonical version of text file
            try:                
                with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')]+'/'+accession+'.txt','wb') as out:
                          out.write(pathology_dictionary[mrn][accession][(-1,'FullText',0,None)])
            except:
                return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR in process_pathology attempting to write text to file at'+ \
                        arguments.get('-f')[:arguments.get('-f').find('.nlp')] +'/'+accession+'.txt - unknown number of reports completed. '+str(sys.exc_info()[1])}],list)

            ## find disease group in the case of unknown/all --- this is currently simply looking for keywords in the full text
            ## of the pathology report - future work to include section specific search and stochastic language model
            if arguments.get('-g')=='all':
                disease_group,derived_disease_group_confidence = PathClassifier.classify(pathology_dictionary[mrn][accession][(-1,'FullText',0,None)])               
                disease_group_data_dictionary = get_disease_specific_dictionary(disease_group)
                field_value_dictionary[global_strings.DZ_GROUP]={global_strings.VALUE:disease_group,global_strings.CONFIDENCE:('%.2f' % derived_disease_group_confidence)}
            return_fields,return_errors,return_type=get_fields(disease_group,pathology_dictionary[mrn][accession],disease_group_data_dictionary,path_data_dictionary)
            
            i+=1
            ## if there are no Exceptions and the "no algorithm" isn't there, then run appropriate algorithms
            if return_type!=Exception:
                if arguments.get('-a')=='n':
                    pass
                else:                    
                    field_value_dictionary[global_strings.TABLE+'s']=final_logic.get(return_fields)                  
                field_value_output.append(field_value_dictionary)
            else:                
                return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR in process_pathology.get(fields) -  \
                        unknown number of reports completed.  Return error string: '+return_errors[global_strings.ERR_STR]}],list)           

    return (field_value_output,return_errors,list)

