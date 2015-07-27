#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathStageM1.0'
import re
import global_strings

def get(disease_group,dictionary):
    try:
        '''
        extract the pathological M Stage (evidence of metastasis)from normal cased text of the pathology report        
        '''
        return_dictionary={global_strings.NAME:"PathStageM",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,
                           global_strings.VERSION:__version__,global_strings.STARTSTOPS:[],global_strings.TABLE:global_strings.STAGE_GRADE_TABLE}
                                                                                           


        full_text=dictionary[(-1,'FullText',0,None)]
        m_stage=re.match('.*(pM[012x]).*',full_text,re.DOTALL)
        if m_stage:
            return_dictionary[global_strings.VALUE]=m_stage.group(1)
            return_dictionary[global_strings.STARTSTOPS].append({global_strings.START:m_stage.start(),global_strings.STOP:m_stage.end()})
        return ([return_dictionary],list)
    except:
        return ({global_strings.ERR_TYPE:'Warning',global_strings.ERR_STR:'ERROR in PathStageM module. '},Exception)
