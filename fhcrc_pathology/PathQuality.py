#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathQuality1.0'


import re
import global_strings
from datetime import datetime

def get(disease_group,dictionary):
    '''
    extract evidence of a reviewed report cased text of the pathology report    
    '''
    
    return_dictionary={global_strings.NAME:"PathQuality",global_strings.KEY:"ALL",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[],global_strings.TABLE:global_strings.PATHOLOGY_TABLE}
                       
    full_text=dictionary[(-1,'FullText',0,None)]
    
    ## make this match non greedy so that the first date is picked out
    review_match=re.finditer(r' (consult|outside institution|reviewed at uwmc|reviewed at university of washington|slide review) ',full_text.lower(),re.DOTALL)
    start_stops_set=set([])
    for each in review_match:                               
        return_dictionary[global_strings.VALUE]='REV'        
        start_stops_set.add((each.start(1),each.end(1)))
    if return_dictionary[global_strings.VALUE]:
        return_dictionary[global_strings.STARTSTOPS]=[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in start_stops_set]    
        return_dictionary[global_strings.CONFIDENCE]=("%.2f" % .98)
    else:
         return_dictionary[global_strings.VALUE]='STD'
         return_dictionary[global_strings.CONFIDENCE]=("%.2f" % .90)
         return_dictionary[global_strings.STARTSTOPS]=[]
    return ([return_dictionary],list) 
