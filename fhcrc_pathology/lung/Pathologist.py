#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''October 2014'''
__version__='Pathologist1.0'

import re

def get(dictionary):
    '''
    extract the (first) pathologist's name from the end of the report    
    return a dictionary of
    {"name":"Pathologist",
    "value":datetime object/or None,
    "algorithmVersion": __version__,
    "confidence": confidence_value,
    "startStops":[{"startPosition":start_pos1,"stopPostiion":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"Pathologist","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    
    
    ignore_section=sorted([(x,y) for z in dictionary.keys() for x,y in dictionary[z].items()],key=lambda b:int(b[0]))
    
    text='\n'.join([a[1] for a in ignore_section])
    
    ## make this match non greedy so that the initial pathologist is picked out
    name_match=re.match('.*?\n([A-Za-z\'\-,. ]+) MD[ A-Za-z, ]*\n[ ]*Pathologist[ ]*\n.*',text,re.DOTALL)    
    if name_match:        
        return_dictionary["value"]=name_match.group(1)
        return_dictionary["confidence"]=1.0
        return_dictionary["startStops"].append({"startPosition":name_match.start(1),"stopPosition":name_match.end(1)})
    
    return (return_dictionary,dict)
