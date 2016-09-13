'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class CellularityType(OneFieldPerReport):
    ''' extract the cellularity type (hypo, hyper, normal) '''
    __version__ = 'CellularityType1.0'

    def __init__(self):
        super(CellularityType, self).__init__()
        self.field_name = 'CellularityType'
        self.table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.85
        self.unlabled_specimen_confidence = 0.7
        ## reference lists & dictionaries ##
        self.file_name_string = 'cellularity'
        self.regex = r'(.)'
        self.value_type = 'match'
        self.match_style = 'all'