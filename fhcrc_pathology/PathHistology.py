'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings as gb

class PathHistology(OneFieldPerSpecimen):
    ''' find a disease specific (or back off to a general) histology from the path text '''
    __version__ = 'PathHistology1.0'
    def __init__(self):
        super(PathHistology, self).__init__()
        self.specimen_field_name = 'PathFindHistology'
        self.overall_field_name = 'PathHistology'
        self.specimen_table = gb.FINDING_TABLE
        self.overall_table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.9
        self.unlabled_specimen_confidence = 0.7
        ## reference lists & dictionaries ##
        self.file_name_string = 'histologies'
        ## relevant sections of the report ##
        self.good_section = r'IMPRESSION|FINAL DIAGNOSIS|COMMENT|DX|SUMMARY CANCER'
        self.bad_section = r'CLINICAL|Note'

        ## there is a secondary data element that should be searched for
        ## based on either position or value of the first e.g. PathGrade
        self.has_secondary_data_element = True
        self.secondary_data_elements = ['PathGrade']
