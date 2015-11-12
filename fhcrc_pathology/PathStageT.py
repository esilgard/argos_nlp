'''author@esilgard'''
#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#


from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class PathStageT(OneFieldPerReport):
    ''' extract explicit mentions of pathological tumor staging '''
    __version__ = 'PathStageT1.0'
    def __init__(self):
        super(PathStageT, self).__init__()
        self.field_name = 'PathStageT'
        self.regex = r'((p|y|[pP]athological)[ ]*T[012345][abc]?)'
        self.confidence = .98
        self.match_style = 'all'
        self.table = gb.STAGE_GRADE_TABLE
        self.value_type = 'match'
