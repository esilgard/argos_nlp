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

''' author @ esilgard '''

'''
    based off basic pathology parser program - ammended to process scca cytogenetics text from...Gateway?
'''
__version__='scca_cyto_parser1.0'

import re,sys,global_strings

## header names coming from the SCCA karyo from Gateway ##
required_header_set=set([global_strings.KARYO,global_strings.ACCESSION_NUM,global_strings.UWID])


def parse(obx_file):
    '''
    this is a basic parser scca cytogenetics reports
    input = "obx_file" = a tab delimited text version of the gateway? cytogenetics table - one line per karyotype report
    output = "cytogenetics_dictionary" = a dictionary of {unique UWID:{unique ACCESSION_NUM:{(section order, section heading, character onset of section):{row num:KARYO(text)}}}}

    **to work correctly first line must contain the expected headers**
    --returns a tuple of output, return_type
    '''
    
    cytogenetics_dictionary={}
    section='ISCN Diagnosis'
    section_order=0
    try:       
        OBX=open(obx_file,'rU').readlines()        
        OBX=[re.sub('[\r\n]','',a).split('\t') for a in OBX]        
        header_set= set(OBX[0])
        
        if set(header_set)>=(required_header_set):           
            headers=dict((k,v) for v,k in enumerate(OBX[0]))            
            try:
                # sort records by MRN_CAPS, accession, and then setid - ignore null MRN_CAPSs, accessions, or setids
                OBX=sorted([y for y in OBX[1:] if (y[headers.get(global_strings.UWID)]!='NULL' and y[headers.get(global_strings.ACCESSION_NUM)]!='NULL')],\
                            key=lambda x: (x[headers.get(global_strings.UWID)],x[headers.get(global_strings.ACCESSION_NUM)]))

                chars_onset=0                
                for line in OBX:                    
                    mrn=line[headers.get(global_strings.UWID)]                   
                    accession=line[headers.get(global_strings.ACCESSION_NUM)]
                    index=0   #there is only one line perreport, so index is always zero - parser is here just to maintain consistent output format to uw reports
                    
                    text=line[headers.get(global_strings.KARYO)]
                   
                    if global_strings.ACCESSION_NUM in line:
                        # ignore duplicate header lines
                        pass                                                                  
                    elif  text=='NULL':                         
                        # maintain readability of fully constituted text by keeping empty 'NULL' lines 
                        cytogenetics_dictionary[mrn]=cytogenetics_dictionary.get(mrn,{})
                        cytogenetics_dictionary[mrn][accession]=cytogenetics_dictionary[mrn].get(accession,{})
                        cytogenetics_dictionary[mrn][accession][(-1,'FullText',0,None)]=cytogenetics_dictionary[mrn][accession].get((-1,'FullText',0,None),'')  +'\n'
                        chars_onset+=1                                                       
                    else:
                        
                        ## grab accession dictionary
                        cytogenetics_dictionary[mrn]=cytogenetics_dictionary.get(mrn,{})                        
                        cytogenetics_dictionary[mrn][accession]=cytogenetics_dictionary[mrn].get(accession,{})
                        index=0
                        chars_onset=0
                        specimen=''
                        section_order=0
                        specimen_dictionary={'NA':'NA'}                                                        
                        section_header='ISCN Diagnosis'             
                                                      
                        cytogenetics_dictionary[mrn][accession][(section_order,section,chars_onset,specimen)]=cytogenetics_dictionary[mrn][accession].get((section_order,section,chars_onset,specimen),{})                
                        cytogenetics_dictionary[mrn][accession][(section_order,section,chars_onset,specimen)][index]=text
                        cytogenetics_dictionary[mrn][accession][(-1,'FullText',0,None)]=cytogenetics_dictionary[mrn][accession].get((-1,'FullText',0,None),'')+text+'\n'
                        chars_onset+=len(text)+1
                   
                return cytogenetics_dictionary,dict
            except:
                return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" \n trouble parsing "+str(obx_file)+" -- program aborted"},Exception)
        else:
            return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" \n required field headers not found in inital line of "+str(obx_file)+" -- must include "+\
                     ','.join(required_header_set-header_set)+" -- program aborted"},Exception)      
    except:        
        return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" \n could not find input file "+str(obx_file)+" -- program aborted"},Exception)
        


            
   

                       


   

                       

