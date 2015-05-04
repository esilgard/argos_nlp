#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''November 2013'''
__version__='PathDate1.0'


import re
from datetime import datetime

def get(disease_group,dictionary):
    '''
    extract the signed date from normal cased text of the pathology report
    return a dictionary of
        {"name":"PathDate",
        "value":datetime object/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathDate","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
                       
    full_text=dictionary[(-1,'FullText',0,None)]
    
    ## make this match non greedy so that the first date is picked out
    date_match=re.match('.*?Electronically signed[ ]*([\d]{1,2})[\-/]([\d]{1,2})[\-/]([\d]{4}).*',full_text,re.DOTALL)
    if date_match:
        year=date_match.group(3)
        month=date_match.group(1)
        day=date_match.group(2)
        if len(date_match.group(2))==1:               
            day='0'+date_match.group(2)                
        return_dictionary["value"]=str(datetime.strptime(year+','+month+','+day,'%Y,%m,%d'))
        return_dictionary["confidence"]=1.0
        return_dictionary["startStops"].append({"startPosition":date_match.start(1),"stopPosition":date_match.end(3)})
           
    return ([return_dictionary],list) 
