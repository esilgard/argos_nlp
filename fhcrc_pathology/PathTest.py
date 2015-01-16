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
###**** table=PathTest ***###
__version__='PathTest1.0'

def get(disease_group,dictionary):
    '''
    extract the pathology tests from normal cased text of the pathology report
    
    '''
    return_dictionary_list=[]
    

    full_text=dictionary[(-1,'FullText',0,None)]
    return (return_dictionary_list,list) 
