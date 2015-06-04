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

import sys
import os,re,global_strings,clinical_parser,prognostic_staging_pipeline

'''author@esilgard'''
__version__='process_clinical1.0'

def main(arguments,path):
   
    '''
    current minimum required flags for the clinical note parsing in the "arguments" dictionary are:
        -f input clinical file
        -g disease group    
    '''
                                               
    try:
        clinical_dictionary,return_type=clinical_parser.parse(arguments.get('-f'))        
        if return_type!=dict:
            return ({},clinical_dictionary,Exception)
    except:        
        return({},[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR: could not complete clinical_parser module '\
               +' --- program aborted.'+str(sys.exc_info())}],Exception)   
    
    disease_group=arguments.get('-g')   
    field_value_output=[]
    error_output=[]
    return_error_list=[]
    i=0
    ## create a list of output field dictionaries ##
    for mrn in clinical_dictionary:
        print mrn
        print len(clinical_dictionary[mrn]),'notes for patient'
        ## feeds in a list of tuples (note_id,note_text) where note id is a tuple of (mrn,service datetime, updated datetime) TEMPORARY and note_text is the text clinic note blob                         
        return_fields,return_errors,return_type=prognostic_staging_pipeline.get(arguments.get('-g'),clinical_dictionary[mrn])
        if return_type!=Exception:
            field_value_dictionary={}
            field_value_dictionary[global_strings.MRN]=mrn
            field_value_dictionary[global_strings.TABLE+'s']=return_fields
            field_value_output.append(field_value_dictionary)
            if return_errors: return_error_list.append(return_errors)
        else:
            return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:\
                         ' FATAL ERROR in process_clinical.get() - unknown number of reports completed.'+str(sys.exc_info())}],list) 

        # output text files (and metadata elements? - maybe in parent loop)
        for each_record in clinical_dictionary[mrn]:            
            note_id=each_record[0]
            note_text=each_record[1]
            filename=arguments.get('-f')[:arguments.get('-f').find('.nlp')]+'/'+'_'.join([str(x) for x in note_id]).replace(' ','_').replace(':','_')+'.txt'
            try:                
                with open(filename,'wb') as out:                    
                    out.write(note_text)
            except:                                
                return (field_value_output,[{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'FATAL ERROR in process_clinical attempting to write text to file at '+ \
                    filename+' - unknown number of reports completed. '+str(sys.exc_info())}],list)
                      
        print ''
    return (field_value_output,return_error_list,list)
