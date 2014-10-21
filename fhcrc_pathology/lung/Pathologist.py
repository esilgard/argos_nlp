#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''last update October 2014'''
__version__='Pathologist1.0'

import re

def get(dictionary):
    '''
    extract the pathologist's name from the end of the report   
    
    return a dictionary of
        {"name":"Pathologist",
        "value":datetime object/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"Pathologist","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    
    text='\n'.join([y for x in dictionary.keys() for x,y in sorted(dictionary[x].items())])    
    name_match=re.match('.*\n([A-Za-z\'\- ]+) MD[ A-Za-z., ]*\n[ ]*Pathologist[ ]*\n.*',text,re.DOTALL)    
    if name_match:
       return_dictionary["value"]=name_match.group(1)      
       return_dictionary["confidence"]=("%.2f" % 1.0)
       return_dictionary["startStops"].append({"startPosition":name_match.start(1),"stopPostion":name_match.end(1)})
   
    return return_dictionary
