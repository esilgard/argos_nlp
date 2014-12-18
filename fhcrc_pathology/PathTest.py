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
###**** table=PathTest ***###
__version__='PathTest1.0'

def get(disease_group,dictionary):
    '''
    extract the pathology tests from normal cased text of the pathology report
    return a dictionary of
        {"name":"PathTest",
        "value":test name/result? None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "table":table_name,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary_list=[]
    

    full_text=dictionary[(-1,'FullText',0,None)]
    return (return_dictionary_list,list) 
