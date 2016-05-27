'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class ClinicalHistory(OneFieldPerReport):
    ''' find the signed date in the pathology report '''
    __version__ = 'ClinicalHistory1.0'
    def __init__(self):
        super(ClinicalHistory, self).__init__()
        self.field_name = 'ClinicalHistory'
        self.regex = r'(history of |hx of |clinical indication ).{,30}'
        self.confidence = 1
        self.match_style = 'all'
        self.table = gb.PATHOLOGY_TABLE
        self.value_type = 'match'
        ## reference lists & dictionaries ##
        self.file_name_string = 'histologies'
