'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings as gb

class ClinicalHistory(OneFieldPerSpecimen):
    '''
        find a clinical history of disease (specific to the current disease at first,then back off to more general)
        because the only section this algorithm should look in is the clinical history, it will always yield a value
        for the 'UNK' specimen and roll up to the report level
    '''
    __version__ = 'ClinicalHistory1.0'
    def __init__(self):
        super(PathHistology, self).__init__()
        self.specimen_field_name = 'ClinicalFindHistory'
        self.overall_field_name = 'ClinicalHistory'
        self.specimen_table = gb.FINDING_TABLE
        self.overall_table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.5
        self.unlabled_specimen_confidence = 0.5
        ## reference lists & dictionaries ##
        self.file_name_string = 'histologies'
        ## relevant sections of the report ##
        self.good_section = r'CLINICAL|HX|HISTORY|History'
        self.good_section = r'FINAL DIAGNOSIS|DX'

