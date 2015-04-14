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
    based off basic pathology parser program - for UW pathology reports from Amalga
'''
__version__='uw_cyto_parser1.0'

import re,sys,global_strings

required_header_set=set([global_strings.SET_ID,global_strings.OBSERVATION_VALUE,global_strings.FILLER_ORDER_NO,global_strings.MRN_CAPS])


def parse(obx_file):
    '''
    this is a basic parser and sectioner for  Amalga pathology reports
    input = "obx_file" = a tab delimited text version of an Amalga OBX table
    output = "cytogenetics_dictionary" = a dictionary of {unique MRN_CAPSs:{unique FILLER_ORDER_NOs:{(section order, section heading, character onset of section):{row num/SET_ID:texts}}}}

    **to work correctly first line must contain the expected headers**
    --returns a tuple of output, return_type
    '''
    
    cytogenetics_dictionary={}
    section='NULL'
    section_order=0
    try:       
        OBX=open(obx_file,'rU').readlines()        
        OBX=[re.sub('[\r\n]','',a).split('\t') for a in OBX]        
        header_set= set(OBX[0])
        
        if set(header_set)>=(required_header_set):           
            headers=dict((k,v) for v,k in enumerate(OBX[0]))            
            try:
                # sort records by MRN_CAPS, accession, and then setid - ignore null MRN_CAPSs, accessions, or setids
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
                        if index=='1':
                            chars_onset=0
                            ## create a specimen source dictionary for each labeled specimen (in the same format as the regular pathology section dictionary ##
                            try:
                                specimen_dictionary=dict((x.split(')')[0],x.split(')')[1].replace('(',' ')) for x in  line[headers.get(global_strings.SPECIMEN_SOURCE)].strip('"').split('~'))
                            except:
                                specimen_dictionary={'NA':'NA'}
                            cytogenetics_dictionary[mrn][accession][(0,global_strings.SPECIMEN_SOURCE,0,None)]={}                            
                            cytogenetics_dictionary[mrn][accession][(0,global_strings.SPECIMEN_SOURCE,0,None)][0]=cytogenetics_dictionary
                            
                        section_header=re.match('[\*\" ]*([A-Za-z ]+)[\*:]+',text)              # match general section header patterns                        
                        # reassign the section variable if you find a section pattern match, reset specimen and increment section order
                        if section_header: section=section_header.group(1).strip();section_order+=1;specimen=''
                        specimen_header=re.match('[\s\"]{,4}([,A-Z\- and&]+?)[\s]*(FS)?[\s]*[)].*',text)                        
                        if specimen_header:                          
                            specimen='' ## reset specimen if there is a new specimen header match
                            M=specimen_header.group(1).replace(' ','')                                                    
                            for each in  specimen_dictionary.keys():                                
                                if re.search('['+M+']',each):
                                    specimen+=each                                
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
        


            
   

                       

