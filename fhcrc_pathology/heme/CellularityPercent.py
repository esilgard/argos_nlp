'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from ..OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class CellularityPercent(OneFieldPerReport):
    ''' extract the cellularity percentage(s)'''
    __version__ = 'CellularityPercent1.0'
    def __init__(self):
        super(CellularityPercent, self).__init__()
        self.field_name = 'CellularityPercent'
        self.table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.85
        self.unlabled_specimen_confidence = 0.7
        ## relevant sections of the report ##
        self.regex = r'Cellularity:[ ]+[\w\d ]*([1-9][\d]?([ \-]+[\d]{1,2})?)%'
        self.value_type = 'match'
        self.match_style = 'all'