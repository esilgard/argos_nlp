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

import sys,os,re,global_strings
from datetime import datetime
'''author@esilgard'''
__version__='clinical_parser1.0'


## turn ISO formatted datetime strings into datetime objects
def make_datetime(date):
    date=datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')    
    return date



def parse(input_note_file):    
    '''
    take input tab delimited file of patient notes and parse
    into a dictionary of
    {mrn:[(datetime,description,note_text),...]....}
    '''
    ## header names exptected to be coming from the Amalga Import ##
    required_header_set=set([global_strings.MRN_CAPS,global_strings.EVENT_DESC,global_strings.SERVICE_DATE,global_strings.UPDATE_DATE,global_strings.BLOB])

    note_dictionary={}
    try:
        
        NOTES=open(input_note_file,'rU').readlines()        
        NOTES=[re.sub('[\r\n]','',a).split('\t') for a in NOTES]        
        header_set= set(NOTES[0])
        ## create a dictionary of headers and their indices (location in each line)
        if set(header_set)>=(required_header_set):           
            headers=dict((k,v) for v,k in enumerate(NOTES[0]))
            for line in NOTES:
                ## skip over any header lines (will catch duplicate header lines as well)
                if global_strings.EVENT_DESC not in line and len(line)>3:
                    try:                        
                        mrn=line[headers.get(global_strings.MRN_CAPS)]
                        note_dictionary[mrn]=note_dictionary.get(mrn,[])
                        ## FOR NOW - treating the tuple of mrn, service date and update DATETIME as a unique identifier                        
                        service_datetime=make_datetime(line[headers.get(global_strings.SERVICE_DATE)])                        
                        update_datetime=make_datetime(line[headers.get(global_strings.UPDATE_DATE)])                        
                        note_id=(mrn,service_datetime,update_datetime)                        
                        note_dictionary[mrn].append((note_id,line[headers.get(global_strings.BLOB)]))                        
                    except:                    
                        return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"FATAL ERROR: "+str(sys.exc_info()[0])+", "+str(sys.exc_info()[1])+\
                         " errors encountered parsing input file -- program aborted"},Exception)
           
            print len(note_dictionary),'patients with notes'
            return (note_dictionary,dict)
        else:
            return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"FATAL ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+\
                     " required field headers not found in inital line of "+str(input_note_file)+" -- must include "
                     ','.join(required_header_set-header_set)+" -- program aborted"},Exception)      
    except:        
        return ({global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:"FATAL ERROR: "+str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+\
                 " -- could not find input file "+str(input_note_file)+" -- program aborted"},Exception)
        
