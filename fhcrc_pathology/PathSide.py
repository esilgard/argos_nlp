'''author@esilgard'''
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings as gb

class PathSide(OneFieldPerSpecimen):
    ''' extract the laterality (side) of each specimen, where applicable '''
    __version__ = 'PathSide1.0'

    def __init__(self):
        super(PathSide, self).__init__()
        self.specimen_field_name = 'PathFindSide'
        self.overall_field_name = 'PathSide'
        self.specimen_table = gb.FINDING_TABLE
        self.overall_table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.97
        self.unlabled_specimen_confidence = 0.9
        ## reference lists & dictionaries ##
        self.file_name_string = 'sides'
        ## relevant sections of the report ##
        self.good_section = r'SPECIMEN|Specimen|DESCRIPTION|IMPRESSION|DIAGNOSIS|DX|DESC|GROSS'
        self.bad_section = r'CLINICAL|Note'
        ## ability to infer new value from one or more existing ones
        self.inference_flag = True

    def infer(self, finding_set):
        ''' infer 'bilateral' if the finding set is specifically only 'right' and 'left' '''
        if finding_set == set(['Right', 'Left']):
            finding_set = set(['Bilateral'])
        return finding_set
