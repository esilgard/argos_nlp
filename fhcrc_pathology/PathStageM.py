'''author@esilgard'''
#
# Copyright (c) 2014-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class PathStageM(OneFieldPerReport):
    ''' extract the explicit metastasis stage (different than finding evidence of metastasis'''
    __version__ = 'PathStageM1.0'
    def __init__(self):
        super(PathStageM, self).__init__()
        self.field_name = 'PathStageM'
        self.regex = r'(([PpYy]|[pP]athological)[ ]*M[012Xx])'
        self.confidence = .90
        self.match_style = 'all'
        self.table = gb.STAGE_GRADE_TABLE
        self.value_type = 'match'
