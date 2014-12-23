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
__version__='PathStageT1.0'
import re


def get(disease_group,dictionary):
    try:
      
        '''
        extract the PathStageT (size/location of tumor)from normal cased text of the pathology report
        return a dictionary of
            {"name":"PathStageT",
            "value":datetime object/or None,
            "algorithmVersion": __version__,
            "confidence": confidence_value,
            "table":table_name,
            "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
        '''
        full_text=dictionary[(-1,'FullText',0,None)]        
        return_dictionary={"name":"PathStageT","value":None,"confidence":0.0,"algorithmVersion":__version__,
                           "startStops":[],"table":"PathologyStageGrade"}
        
        
        t_stage=re.match('.*(pT[012345][abc]?).*',full_text,re.DOTALL)        
       
        if t_stage:
            return_dictionary["value"]=t_stage.group(1)
            return_dictionary["startStops"].append({"startPosition":t_stage.start(),"stopPosition":t_stage.end()})
        return ([return_dictionary],list)
    except:
        return ({'errorType':'Warning','errorString':'ERROR in PathStageT module.'},Exception)
