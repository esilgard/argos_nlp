#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OneFieldPerReport import OneFieldPerReport
import global_strings as dict_keys

class PathStageSystem(OneFieldPerReport):    
    __version__='PathStageSystem1.0' 	

    def __init__(self):
        self.field_name='PathStageSystem'
        self.regex=r'(AJCC[ ,]+[0-9]{1,2})[ thsnd]+ed'
        self.confidence= .95
	self.match_style='all'
	self.table=dict_keys.STAGE_GRADE_TABLE
	self.value_type='match'	
	
