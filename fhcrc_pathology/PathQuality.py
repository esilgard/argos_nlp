#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''


from OneFieldPerReport import OneFieldPerReport
import global_strings as dict_keys

class PathQuality(OneFieldPerReport):    
    __version__='PathQuality1.0'	

    def __init__(self):
        self.field_name='PathQuality'
        self.regex=r'(Consult|[Oo]utside institution|[Rr]eviewed at UWMC|[Rr]eviewed at University of Washington|[Ss]lide review)'        
	self.match_style='all'
	self.confidence=.00     ## this should always be overwritten
	self.table=dict_keys.PATHOLOGY_TABLE
	## this value switches depending on the presence of a pattern match
	## if match==True then value and confidence 1, else 2
	## this means value and confidence 2 are based on the absense of information
	self.value_type={True:('REV',.98),False:('STD',.90)}
	

