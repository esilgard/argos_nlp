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
''' written 2013, last update Oct 2014 '''
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
    output = "pathology_dictionary" = a dictionary of {unique mrns:{unique accession_nums:{section headings:{row nums/index:texts}}}}

    **to work correctly first line must contain headers**

    --returns a tuple of output, return_type
    '''
    
    pathology_dictionary={}
    section='NULL'
    try:
        OBX=open(obx_file,'r').readlines()
        if INDEX in OBX[0]:           
            headers=dict((k,v) for v,k in enumerate(OBX[0].strip().split('\t')))            
            try:
                OBX=sorted(OBX[1:],key=lambda x: (x[headers.get(MRN)],x[headers.get(ACCESSION_NUM)],x[headers.get(INDEX)]))
                
                for line in OBX:                    
                    line=line.split('\t')
                    mrn=line[headers.get(MRN)]                    
                    accession=line[headers.get(ACCESSION_NUM)]                    
                    if accession =='NULL' or ACCESSION_NUM in line:   pass                                           # ignore mrns with no accession and duplicate header lines
                    else:                        
                        pathology_dictionary[mrn]=pathology_dictionary.get(mrn,{})
                        text=line[headers.get(TEXT)]
                        pathology_dictionary[mrn][accession]=pathology_dictionary[mrn].get(accession,{})
                        pathology_dictionary[mrn][accession]['SpecimenSource']={}
                        pathology_dictionary[mrn][accession]['SpecimenSource']['1']=line[headers.get(SPECIMEN)]
                        
                        section_header=re.match('[\*\" ]*([A-Z ]+)[\*:]+',text)                                      # match general section header patterns                       
                        if section_header: section=section_header.group(1).strip()                                   # reassign the section variable if you find a section pattern match
                        pathology_dictionary[mrn][accession][section]=pathology_dictionary[mrn][accession].get(section,{})                
                        pathology_dictionary[mrn][accession][section][line[headers.get(INDEX)]]=text
                        
                return pathology_dictionary,dict
            except:
                return ({'errorType':'Exception','errorString':"ERROR: trouble parsing "+str(obx_file)+" -- program aborted"},Exception)
        else:
            return ({'errorType':'Exception','errorString':"ERROR: field headers not found in inital line of "+str(obx_file)+" -- program aborted"},Exception)      
    except:        
        return ({'errorType':'Exception','errorString':"ERROR: "+str(sys.exc_info()[0])+" -- could not find input file "+str(obx_file)+" -- program aborted"},Exception)
        


            
   

                       

