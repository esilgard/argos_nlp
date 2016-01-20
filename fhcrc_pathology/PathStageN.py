'''author@esilgard'''
#
# Copyright (c) 2014-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class PathStageN(OneFieldPerReport):
    ''' extract the explicit  node staging '''
    __version__ = 'PathStageN1.0'
    def __init__(self):
        super(PathStageN, self).__init__()
        self.field_name = 'PathStageN'
        self.regex = r'((p|y|[pP]athological)[ ]*N[0123Xx][abc]?)'
        self.confidence = .92
        self.match_style = 'all'
        self.table = gb.STAGE_GRADE_TABLE
        self.value_type = 'match'
