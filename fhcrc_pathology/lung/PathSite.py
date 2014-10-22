#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''November 2013, last update October 2014'''
__version__='PathSite1.0'

def get(dictionary):
    '''
    extract the PathSite (location of tumor)from normal cased text of the pathology report
    return a dictionary of
        {"name":"PathSite",
        "value":datetime object/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathSite","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    return (return_dictionary,dict) 

