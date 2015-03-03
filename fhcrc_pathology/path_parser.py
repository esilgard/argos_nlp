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
''' written 2013 '''

''' last update Nov 2014
    - added section order to to the section heading
    - SpecimenSource column from OBR as section (first section, section order=0)
    - stripped all NULL lines (to avoid character offset issues when interpreting NULL as a string) and replaced with a single carriage return
'''
__version__='path_parser1.0'

import re,sys,global_strings,os

## header names exptected to be coming from the Amalga Import ##
required_header_set=set([global_strings.SET_ID,global_strings.OBSERVATION_VALUE,global_strings.SPECIMEN_SOURCE,global_strings.FILLER_ORDER_NO,global_strings.MRN_CAPS])

def parse(obx_file):
    '''
    this is a basic parser and sectioner for  Amalga pathology reports
    input = "obx_file" = a tab delimited text version of an Amalga OBX table
    output = "pathology_dictionary" = a dictionary of {unique mrns:{unique accession_nums:{(section order, section heading, character onset of section):{row num/index:texts}}}}

    **to work correctly first line must contain the expected headers**
    --returns a tuple of output, return_type
    '''
    
    pathology_dictionary={}
    section='NULL'
    section_order=0
    try:
        OBX=open(obx_file,'rU').readlines()        
        OBX=[re.sub('[\r\n]','',a).split('\t') for a in OBX]
        
        header_set= set(OBX[0])
        
        if set(header_set)>=(required_header_set):           
            headers=dict((k,v) for v,k in enumerate(OBX[0]))
            
            try:
                # sort records by mrn, accession, and then setid - ignore null mrns, accessions, or setids
                OBX=sorted([y for y in OBX[1:] if (y[headers.get(global_strings.MRN_CAPS)]!='NULL' and y[headers.get(global_strings.FILLER_ORDER_NO)]!='NULL' and y[headers.get(global_strings.SET_ID)]!='NULL')],\
                            key=lambda x: (x[headers.get(global_strings.MRN_CAPS)],x[headers.get(global_strings.FILLER_ORDER_NO)],int(x[headers.get(global_strings.SET_ID)])))

                chars_onset=0                
                for line in OBX:       
                    mrn=line[headers.get(global_strings.MRN_CAPS)]                   
                    accession=line[headers.get(global_strings.FILLER_ORDER_NO)]
                    index=line[headers.get(global_strings.SET_ID)]
                    if index=='1':section_order=0;chars_onset=0
                    text=line[headers.get(global_strings.OBSERVATION_VALUE)]
                    
                    if global_strings.FILLER_ORDER_NO in line:
                        pass                                                                  # ignore duplicate header lines
                    elif  text=='NULL':
                        # maintain readability of fully constituted text by keeping empty 'NULL' lines 
                        pathology_dictionary[mrn]=pathology_dictionary.get(mrn,{})
                        pathology_dictionary[mrn][accession]=pathology_dictionary[mrn].get(accession,{})
                        pathology_dictionary[mrn][accession][(-1,'FullText',0,None)]=pathology_dictionary[mrn][accession].get((-1,'FullText',0,None),'')  +'\n'
                        chars_onset+=1                                                        # maintain readability of fully constituted text by keeping 'NULL' lines
                    else:
                        ## grab accession dictionary
                        pathology_dictionary[mrn]=pathology_dictionary.get(mrn,{})                        
                        pathology_dictionary[mrn][accession]=pathology_dictionary[mrn].get(accession,{})
                        if index=='1':
                            chars_onset=0                            
                            specimen_dictionary=dict((x.split(')')[0],x.split(')')[1].replace('(',' ')) for x in  line[headers.get(global_strings.SPECIMEN_SOURCE)].strip('"').split('~'))                            
                            pathology_dictionary[mrn][accession][(0,global_strings.SPECIMEN_SOURCE,0,None)]={}                            
                            pathology_dictionary[mrn][accession][(0,global_strings.SPECIMEN_SOURCE,0,None)][0]=specimen_dictionary                                                  

                        section_header=re.match('[\*\" ]*([A-Z ]+)[\*:]+',text)              # match general section header patterns
                        
                        # reassign the section variable if you find a section pattern match, reset specimen and increment section order
                        if section_header: section=section_header.group(1).strip();section_order+=1;specimen=''
                        specimen_header=re.match('[\s\"]{,4}([,A-Z\- ]+?)[\s]*(FS)?[\s]*[)].*',text)            
                        
                        if specimen_header:
                            specimen='' ## reset specimen if there is a new specimen header match
                            M=specimen_header.group(1).replace(' ','')                                                    
                            for each in  specimen_dictionary.keys():                                
                                if re.search('['+M+']',each):
                                    specimen+=each
                        pathology_dictionary[mrn][accession][(section_order,section,chars_onset,specimen)]=pathology_dictionary[mrn][accession].get((section_order,section,chars_onset,specimen),{})                
                        pathology_dictionary[mrn][accession][(section_order,section,chars_onset,specimen)][index]=text
                        pathology_dictionary[mrn][accession][(-1,'FullText',0,None)]=pathology_dictionary[mrn][accession].get((-1,'FullText',0,None),'')+text+'\n'
                        chars_onset+=len(text)+1
                   
                return pathology_dictionary,dict
            except:
                return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"FATAL ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" trouble parsing "+str(obx_file)+" -- program aborted"},Exception)
        else:
            return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"FATAL ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" required field headers not found in inital line of "+str(obx_file)+" -- must include "+\
                     ','.join(required_header_set-header_set)+" -- program aborted"},Exception)      
    except:        
        return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"FATAL ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+" -- could not find input file "+str(obx_file)+" -- program aborted"},Exception)
        
