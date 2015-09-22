#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OneFieldPerReport import OneFieldPerReport
import global_strings as dict_keys

class PathStageN(OneFieldPerReport):
    __version__='PathStageN1.0'
    
    def __init__(self):
        self.field_name='PathStageN'
        self.regex=r'((pN|yN)[0123Xx][abc]?)'
        self.confidence=.92
        self.match_style='all'
        self.table=dict_keys.STAGE_GRADE_TABLE
        self.value_type='match'
