'''author@esilgard'''
#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerReport import OneFieldPerReport
import global_strings as gb

class PathQuality(OneFieldPerReport):
    ''' determine if the pathology report is a review, or in house (based on lack of evidence) '''
    __version__ = 'PathQuality1.0'
    def __init__(self):
        super(PathQuality, self).__init__()
        self.field_name = 'PathQuality'
        self.regex = r'(Consult|[Oo]utside institution|[Rr]eviewed at UWMC|\
                        [Rr]eviewed at University of Washington|[Ss]lide review)'
        self.match_style = 'all'
        self.confidence = .00     ## this should always be overwritten
        self.table = gb.PATHOLOGY_TABLE
        ## this value switches depending on the presence of a pattern match
        ## if match == True then value and confidence 1, else 2
        ## this means value and confidence 2 are based on the absense of information
        self.value_type = {True: ('REV', .98), False: ('STD', .90)}
