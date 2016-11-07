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
        self.confidence = 0.85
        self.less_good_confidence = 0.7
        ## relevant sections of the report ##
        self.good_section = r'BONE MARROW BIOPSY'
        self.less_good_section = r'MARROW DIFFERENTIAL|PARTICLE PREP'
        self.regex = r'[cC]ellularity:[\w\d\t,. ]*?[ ]+([\<\>\~ ]*[\d]+([ \-to]+[0-9]+)?)[ ]*%|([\<\>\~ ]*[\d]+([ \-to]+[0-9]+)?)[ ]*%[\w ]{,15}(total|sampled) cellularity'
        self.value_type = 'match'
        self.match_style = 'all'
        
        
        
