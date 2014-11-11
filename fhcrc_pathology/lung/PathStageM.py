#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''last update October 2014'''
__version__='PathStageM1.0'

def get(dictionary):
        '''
        extract the pathological M Stage (evidence of metastasis)from normal cased text of the pathology report
        return a dictionary of
            {"name":"PathStageM",
            "value": Mstage or None,
            "algorithmVersion": __version__,
            "confidence": confidence_value,
            "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
        '''
        return_dictionary={"name":"PathStageM","value":None,"confidence":0.0,"algorithmVersion":__version__,
                           "startStops":[]}
                           

        
        text=dictionary[(-1,'FullText',0)]   
        return (return_dictionary,dict) 
