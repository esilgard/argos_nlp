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
__version__='PathStageN1.0'
import re

def get(disease_group,dictionary):
    try:        
        '''
        extract the PathStageT (size/location of tumor)from normal cased text of the pathology report
        return a dictionary of
            {"name":"PathStageN",
            "value":datetime object/or None,
            "algorithmVersion": __version__,
            "confidence": confidence_value,
            "table":table_name,
            "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
        '''
        return_dictionary={"name":"PathStageN","value":None,"confidence":0.0,"algorithmVersion":__version__,
                           "startStops":[],"table":"PathologyStageGrade"}
        full_text=dictionary[(-1,'FullText',0,None)]
        print 'pN' in full_text,'pN in text'
        print full_text[full_text.find('pN')-10:full_text.find('pN')+10]
        n_stage=re.match('.*(pN[012345][abc]?).*',full_text,re.DOTALL)
        if n_stage:
            print 'N STAGE MATCH'
            return_dictionary["value"]=n_stage.group(1)            
            return_dictionary["startStops"].append({"startPosition":n_stage.start(),"stopPosition":n_stage.end()})
        return ([return_dictionary],list)
    except:        
        return ({'errorType':'Warning','errorString':'ERROR in PathStageN module.'},Exception)
