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
__version__='PathStageM1.0'
import re

def get(disease_group,dictionary):
    try:
        '''
        extract the pathological M Stage (evidence of metastasis)from normal cased text of the pathology report
        return a dictionary of
                        {"name":"PathStageM",
                        "value": Mstage or None,
                        "algorithmVersion": __version__,
                        "confidence": confidence_value,
                        "table":table_name,
                        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
        '''
        return_dictionary={"name":"PathStageM","value":None,"confidence":0.0,"algorithmVersion":__version__,
                                                                                           "startStops":[],"table":"PathologyStageGrade"}
                                                                                           


        full_text=dictionary[(-1,'FullText',0,None)]
        m_stage=re.match('.*(pM[012x]).*',full_text,re.DOTALL)
        if m_stage:
            return_dictionary["value"]=m_stage.group(1)
            return_dictionary["startStops"].append({"startPosition":m_stage.start(),"stopPosition":m_stage.end()})
        return ([return_dictionary],list)
    except:
        return ({'errorType':'Warning','errorString':'ERROR in PathStageM module. '},Exception)
