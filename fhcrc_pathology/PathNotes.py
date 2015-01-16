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
__version__='PathNotes1.0'
import re
import global_strings
def get(disease_group,dictionary):
    
    '''
    extract the PathNotes from the normal cased text of the pathology report       
    '''
    return_dictionary={global_strings.NAME:"PathNotes",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[],global_strings.TABLE:"PathologyStageGrade"}
    
    full_text=dictionary[(-1,'FullText',0,None)]
    return ([return_dictionary],list) 
