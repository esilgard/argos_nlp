#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#


'''author@esilgard'''
'''November 2013, last update October 2014'''
import re
from datetime import datetime

def get(dictionary):
    '''
    extract the collection date (date of surgery)
    from normal cased text of the pathology report and return a datetime object
    ''' 
    text=' '.join([y for x in dictionary.keys() for y in dictionary[x].values()])
    
    date_match=re.match('.*COLLECTED:[\s]+([A-Z][a-z]{2})[\s]+([\d]{1,2})[\s]+([\d]{4}).*',text)
    
    if date_match:
        year=date_match.group(3)
        month=date_match.group(1)
        day=date_match.group(2)
        if len(date_match.group(2))==1:               
            day='0'+date_match.group(2)                
        return str(datetime.strptime(year+','+month+','+day,'%Y,%b,%d'))
    else: return None
