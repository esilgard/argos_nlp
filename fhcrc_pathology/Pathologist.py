#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written October 2014, updates:
    December 2014 - added table_name to return dictionary
'''
__version__='Pathologist1.0'

import re
import global_strings
def get(disease_group,dictionary):
    '''
    extract the (first) pathologist's name from the end of the report    
    
    '''
    return_dictionary={global_strings.NAME:"Pathologist",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[]}
    
    full_text=dictionary[(-1,'FullText',0,None)]
    
    ## make this match non greedy so that the INITIAL pathologist signature is picked out
    name_match=re.match('.*?\n([A-Za-z\'\-,. ]+) MD[ A-Za-z, ]*\n[ ]*Pathologist[ ]*\n.*',full_text,re.DOTALL)    
    if name_match:        
        return_dictionary[global_strings.VALUE]=name_match.group(1)
        return_dictionary[global_strings.CONFIDENCE]=1.0
        return_dictionary[global_strings.TABLE]='Pathology'
        return_dictionary[global_strings.STARTSTOPS].append({global_strings.START:name_match.start(1),global_strings.STOP:name_match.end(1)})
   
    return ([return_dictionary],list)
