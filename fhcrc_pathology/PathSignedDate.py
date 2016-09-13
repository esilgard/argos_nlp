'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerReport import OneFieldPerReport
import global_strings as gb  

class PathSignedDate(OneFieldPerReport):
    ''' find the signed date in the pathology report '''
    __version__ = 'PathSignedDate1.0'
    def __init__(self):
        super(PathSignedDate, self).__init__()
        self.field_name = 'PathSignedDate'
        self.regex = r'Electronically signed[ ]*([\d]{1,2})[\-/]([\d]{1,2})[\-/]([\d]{4})'
        self.confidence = 1
        self.match_style = 'first'
        self.table =gb.PATHOLOGY_TABLE
        self.value_type = 'match'
        self.date_format_string = '%Y,%m,%d'
