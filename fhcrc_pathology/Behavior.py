'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from .OneFieldPerSpecimen import OneFieldPerSpecimen
from . import global_strings as gb

class Behavior(OneFieldPerSpecimen):
    '''
    general behavior class - finding values like 'in situ', 'malignant', 'benign', etc
    '''
    __version__ = 'Behavior1.0'
    def __init__(self):
        super(Behavior, self).__init__()
        self.specimen_field_name = 'Behavior'
        self.overall_field_name = 'Behavior'
        self.specimen_table = gb.FINDING_TABLE
        self.overall_table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.5
        self.unlabled_specimen_confidence = 0.3
         ## reference lists & dictionaries ##
        self.file_name_string = 'behavior'
        ## relevant sections of the report ##
        self.good_section = r'IMPRESSION|FINAL DIAGNOSIS|COMMENT|FINAL DX|SUMMARY CANCER'
        self.bad_section = r'CLINICAL|Note'
