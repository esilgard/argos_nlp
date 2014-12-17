#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
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
''' written 2013 '''

''' last update Nov 2014
    - added section order to to the section heading
    - SpecimenSource column from OBR as section (first section, section order=0)
    - stripped all NULL lines (to avoid character offset issues when interpreting NULL as a string
'''
__version__='cyto_parser1.0'

import re,sys

## header names coming from the Amalga Import ##
MRN='MRN'
ACCESSION_NUM='FillerOrderNo'
INDEX='SetId'
TEXT='ObservationValue'

required_header_set=set([INDEX,TEXT,ACCESSION_NUM,MRN])


def parse(obx_file):
    '''
    this is a basic parser and sectioner for  Amalga pathology reports
    input = "obx_file" = a tab delimited text version of an Amalga OBX table
    output = "cytogenetics_dictionary" = a dictionary of {unique mrns:{unique accession_nums:{(section order, section heading, character onset of section):{row num/index:texts}}}}

    **to work correctly first line must contain the expected headers**
    --returns a tuple of output, return_type
    '''
    
    cytogenetics_dictionary={}
    section='NULL'
    section_order=0
    try:
        OBX=open(obx_file,'r').readlines()
        OBX=[a.strip().split('\t') for a in OBX]
        
        header_set= set(OBX[0])
        
        if set(header_set)>=(required_header_set):           
            headers=dict((k,v) for v,k in enumerate(OBX[0]))
            
            try:
                # sort records by mrn, accession, and then setid - ignore null mrns, accessions, or setids
                OBX=sorted([y for y in OBX[1:] if (y[headers.get(MRN)]!='NULL' and y[headers.get(ACCESSION_NUM)]!='NULL' and y[headers.get(INDEX)]!='NULL')],\
                            key=lambda x: (x[headers.get(MRN)],x[headers.get(ACCESSION_NUM)],int(x[headers.get(INDEX)])))

                chars_onset=0
                specimen=''
                for line in OBX:       
                    mrn=line[headers.get(MRN)]                   
                    accession=line[headers.get(ACCESSION_NUM)]
                    index=line[headers.get(INDEX)]
                    if index=='1':chars_onset=0
                    text=line[headers.get(TEXT)] 
                    if ACCESSION_NUM in line:
                        pass                                                                  # ignore duplicate header lines
                    elif  text=='NULL':
                        # maintain readability of fully constituted text by keeping empty 'NULL' lines                                              
                        chars_onset+=1                                                       
                    else:
                        ## grab accession dictionary
                        cytogenetics_dictionary[mrn]=cytogenetics_dictionary.get(mrn,{})                        
                        cytogenetics_dictionary[mrn][accession]=cytogenetics_dictionary[mrn].get(accession,{})
                                    
                        cytogenetics_dictionary[mrn][accession][chars_onset]=text
                        cytogenetics_dictionary[mrn][accession][0]=cytogenetics_dictionary[mrn][accession].get(0)+text+'\n'
                        chars_onset+=len(text)+1
                   
                return cytogenetics_dictionary,dict
            except:
                return ({'errorType':'Exception','errorString':"ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" trouble parsing "+str(obx_file)+" -- program aborted"},Exception)
        else:
            return ({'errorType':'Exception','errorString':"ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" required field headers not found in inital line of "+str(obx_file)+" -- must include "+\
                     ','.join(required_header_set-header_set)+" -- program aborted"},Exception)      
    except:        
        return ({'errorType':'Exception','errorString':"ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" -- could not find input file "+str(obx_file)+" -- program aborted"},Exception)
        


            
   

                       

