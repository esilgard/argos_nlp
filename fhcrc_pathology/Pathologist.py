'''author@esilgard'''
#
# Copyright (c) 2014-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class Pathologist(OneFieldPerReport):
    ''' extract the name of the pathologist who initially signed the report '''
    __version__ = 'Pathologist1.0'
    def __init__(self):
        super(Pathologist, self).__init__()
        self.field_name = 'Pathologist'
        self.regex = r'\n([A-Za-z\'\-,. ]+) MD(, PhD)?[ ]*\n[ ]*Pathologist[ ]*\n'
        self.confidence = 1
        self.match_style = 'first'
        self.table = gb.PATHOLOGY_TABLE
        self.value_type = 'match'
