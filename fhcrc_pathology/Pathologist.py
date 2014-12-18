#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
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

def get(disease_group,dictionary):
    '''
    extract the (first) pathologist's name from the end of the report    
    return a dictionary of
    {"name":"Pathologist",
    "value":datetime object/or None,
    "algorithmVersion": __version__,
    "confidence": confidence_value,
    "table":table_name,
    "startStops":[{"startPosition":start_pos1,"stopPostiion":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"Pathologist","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    
    full_text=dictionary[(-1,'FullText',0,None)]
    
    ## make this match non greedy so that the INITIAL pathologist signature is picked out
    name_match=re.match('.*?\n([A-Za-z\'\-,. ]+) MD[ A-Za-z, ]*\n[ ]*Pathologist[ ]*\n.*',full_text,re.DOTALL)    
    if name_match:        
        return_dictionary["value"]=name_match.group(1)
        return_dictionary["confidence"]=1.0
        return_dictionary["table"]='Pathology'
        return_dictionary["startStops"].append({"startPosition":name_match.start(1),"stopPosition":name_match.end(1)})
   
    return ([return_dictionary],list)
