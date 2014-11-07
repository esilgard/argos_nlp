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
__version__='path_parser1.0'

import re,sys

## header names coming from the Amalga Import ##
MRN='MRN'
ACCESSION_NUM='FillerOrderNo'
INDEX='SetId'
TEXT='ObservationValue'
SPECIMEN='SpecimenSource'

def parse(obx_file):
    '''
    this is a basic parser and sectioner for  Amalga pathology reports
    input = "obx_file" = a tab delimited text version of an Amalga OBX table
    output = "pathology_dictionary" = a dictionary of {unique mrns:{unique accession_nums:{(section order, section heading):{row num/index:texts}}}}

    **to work correctly first line must contain the expected headers**

    --returns a tuple of output, return_type
    '''
    
    pathology_dictionary={}
    section='NULL'
    section_order=0
    try:
        OBX=open(obx_file,'r').readlines()
        if INDEX in OBX[0]:           
            headers=dict((k,v) for v,k in enumerate(OBX[0].strip().split('\t')))            
            try:
                OBX=sorted(OBX[1:],key=lambda x: (x[headers.get(MRN)],x[headers.get(ACCESSION_NUM)],int(x[headers.get(INDEX)])))
                
                for line in OBX:
                    
                    line=line.split('\t')                    
                    mrn=line[headers.get(MRN)].strip()                    
                    accession=line[headers.get(ACCESSION_NUM)].strip()
                    index=line[headers.get(INDEX)].strip()
                    if index=='1':section_order=0
                    text=line[headers.get(TEXT)].strip()
                    
                    if accession =='NULL' or ACCESSION_NUM in line or text=='NULL':pass # ignore mrns with no accession, duplicate header lines, and null text sections
                    else:                        
                        pathology_dictionary[mrn]=pathology_dictionary.get(mrn,{})                        
                        pathology_dictionary[mrn][accession]=pathology_dictionary[mrn].get(accession,{})
                        pathology_dictionary[mrn][accession][(0,'SpecimenSource')]={}
                        pathology_dictionary[mrn][accession][(0,'SpecimenSource')]['0']=line[headers.get(SPECIMEN)].strip()
                        
                        section_header=re.match('[\*\" ]*([A-Z ]+)[\*:]+',text)                                      # match general section header patterns                       
                        if section_header: section=section_header.group(1).strip();section_order+=1                  # reassign the section variable if you find a section pattern match
                        pathology_dictionary[mrn][accession][(section_order,section)]=pathology_dictionary[mrn][accession].get((section_order,section),{})                
                        pathology_dictionary[mrn][accession][(section_order,section)][index]=text                       
                return pathology_dictionary,dict
            except:
                return ({'errorType':'Exception','errorString':"ERROR: trouble parsing "+str(obx_file)+" -- program aborted"},Exception)
        else:
            return ({'errorType':'Exception','errorString':"ERROR: field headers not found in inital line of "+str(obx_file)+" -- program aborted"},Exception)      
    except:        
        return ({'errorType':'Exception','errorString':"ERROR: "+str(sys.exc_info()[0])+" -- could not find input file "+str(obx_file)+" -- program aborted"},Exception)
        


            
   

                       

