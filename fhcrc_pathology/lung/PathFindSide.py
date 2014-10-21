#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''last update October 2014'''
__version__='PathFindSide1.0'

def get(dictionary):
    '''
    extract the side/laterality from the text of the pathology report   
    
    return a dictionary of
        {"name":"PathFindSide",
        "value":side or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathFindSide","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    
    
    text='\n'.join([y for x in dictionary.keys()  for x,y in sorted(dictionary[x].items())])
    return return_dictionary
