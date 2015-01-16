#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written November 2013, updates:
    December 2014 - added table_name to return dictionary
'''
__version__='PathDate1.0'


import re
import global_strings
from datetime import datetime

def get(disease_group,dictionary):
    '''
    extract the collection date (date of surgery)from normal cased text of the pathology report
    
    '''
    
    return_dictionary={global_strings.NAME:"PathDate",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[],global_strings.TABLE:'Pathology'}
                       
    full_text=dictionary[(-1,'FullText',0,None)]
    
    ## make this match non greedy so that the first date is picked out
    date_match=re.match('.*?Electronically signed[ ]*([\d]{1,2})[\-/]([\d]{1,2})[\-/]([\d]{4}).*',full_text,re.DOTALL)
    if date_match:
        year=date_match.group(3)
        month=date_match.group(1)
        day=date_match.group(2)
        if len(date_match.group(2))==1:               
            day='0'+date_match.group(2)                
        return_dictionary[global_strings.VALUE]=str(datetime.strptime(year+','+month+','+day,'%Y,%m,%d'))
        return_dictionary[global_strings.CONFIDENCE]=1.0
        return_dictionary[global_strings.STARTSTOPS].append({global_strings.START:date_match.start(1),global_strings.STOP:date_match.end(3)})
        
           
    return ([return_dictionary],list) 
