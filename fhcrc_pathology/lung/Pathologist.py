#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''October 2014'''
VERSION='1.0'

import re

def get(dictionary):
    '''
    extract the pathologist's name from the end of the report
    ''' 
    text='\n'.join([y for x in dictionary.keys() for x,y in sorted(dictionary[x].items())])    
    name_match=re.match('.*\n([A-Za-z\' ]+)\n[ ]*Pathologist[ ]*\n.*',text)    
    if name_match:
        name_match=name_match.group(1).strip()
    return name_match
