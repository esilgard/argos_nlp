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

import sys,uw_cyto_parser,scca_cyto_parser,iscn_parser,iscn_string_cleaner
import os,re,global_strings

'''author@esilgard'''
'''December 2014'''
__version__='process_cytogenetics1.0'

def main(arguments,path):    
    '''
    current minimum required flags for the pathology parsing in the "arguments" dictionary are:
        -f input cytogenetics file
        -g disease group    
    '''
    ## ** temporary hack for now to differentiate between scca and uw reports **##
    if 'uw' in arguments.get('-f'):                                              
        try:
            cytogenetics_dictionary,return_type=uw_cyto_parser.parse(arguments.get('-f'))        
            if return_type!=dict: return ({},cytogenetics_dictionary,Exception)
        except:        
            return({},[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not parse input cytogenetics file '\
                   +arguments.get('-f')+' --- program aborted.'+str(sys.exc_info())}],Exception)
    elif 'scca' in arguments.get('-f'):
        try:
            cytogenetics_dictionary,return_type=scca_cyto_parser.parse(arguments.get('-f'))        
            if return_type!=dict: return ({},cytogenetics_dictionary,Exception)
        except:        
            return({},[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not parse input cytogenetics file '\
                   +arguments.get('-f')+' --- program aborted.'+str(sys.exc_info())}],Exception)
    else:
        return({},[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not parse input cytogenetics file '\
                   +arguments.get('-f')+' --- neither UW nor SCCA specified as a document source --- program aborted.'+str(sys.exc_info())}],Exception)


    disease_group=arguments.get('-g')
   
    field_value_output=[]
    error_output=[]
    return_error_list=[]

    i=0
    ## create a list of output field dictionaries ##
    for mrn in cytogenetics_dictionary:       
        for accession in cytogenetics_dictionary[mrn]:
            #if accession in acc_set:
            cyto_string=''
             ## walk through ISCN section in order (by offsets) incase the cytogenetics string is on multiple, sequential lines
            for sections in sorted(cytogenetics_dictionary[mrn][accession], key=lambda x: x[2]):               
                section_header=sections[1]
                beginning_offset=sections[2]
               
                if 'ISCN' in section_header:                   
                    karyo_offset=beginning_offset
                    for line,text in sorted(cytogenetics_dictionary[mrn][accession][sections].items(),key=lambda x:x[0]):                        
                        cyto_string+=text.strip('"')
            
            if cyto_string:               
                field_value_dictionary={}
                field_value_dictionary[global_strings.REPORT]=accession
                field_value_dictionary[global_strings.MRN]=mrn
                field_value_dictionary[global_strings.DATE]=(cytogenetics_dictionary[mrn][accession][(-1,'Date',0,None)])
               
                karyotype_string=iscn_string_cleaner.get(cyto_string)                
                return_fields,return_errors,return_type=iscn_parser.get(karyotype_string,karyo_offset)
                try:                    
                    exec ('from '+disease_group+' import classify_'+disease_group+'_swog_category')
                    exec('cell_list,swog_return_fields,return_errors=classify_'+disease_group+'_swog_category.get(return_fields,karyotype_string)')
                except:
                    return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:\
                             ' FATAL ERROR in process_cytogenetics.get() - could not retrive disease group specific cytogenetics module'+str(sys.exc_info())}],list)           

                try:                
                    with open(arguments.get('-f')[:arguments.get('-f').find('.nlp')]+'/'+accession+'.txt','wb') as out:
                        out.write(cytogenetics_dictionary[mrn][accession][(-1,'FullText',0,None)])
                except:                                
                    return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR in process_cytogenetics attempting to write text to file at'+ \
                        arguments.get('-f')[:arguments.get('-f').find('.nlp')] +'/'+accession+'.txt - unknown number of reports completed. '+sys.exc_info()}],list)
                if return_type!=Exception:
                    field_value_dictionary[global_strings.TABLES]=[]
                    field_value_dictionary[global_strings.TABLES].append({global_strings.TABLE:disease_group.upper()+'_Cytogenetics',global_strings.FIELDS:swog_return_fields})                    
                    field_value_output.append(field_value_dictionary)
                    if return_errors: return_error_list.append(return_errors)
                else:
                    return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:\
                             ' FATAL ERROR in process_cytogenetics.get() - unknown number of reports completed.'+str(sys.exc_info())}],list)           

    return (field_value_output,return_error_list,list)
