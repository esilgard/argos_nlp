'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings as gb

class PathSite(OneFieldPerSpecimen):
    ''' extract the procedure type "specimen type" from path text '''
    __version__ = 'PathSite1.0'

    def __init__(self):
        super(PathSite, self).__init__()
        self.specimen_field_name = 'PathFindSite'
        self.overall_field_name = 'PathSite'
        self.specimen_table = gb.FINDING_TABLE
        self.overall_table = gb.PATHOLOGY_TABLE
        self.specimen_confidence = 0.85
        self.unlabled_specimen_confidence = 0.7
        ## reference lists & dictionaries ##
        self.file_name_string = 'sites'
        ## relevant sections of the report ##
        self.good_section = r'SPECIMEN|Specimen|IMPRESSION|DIAGNOSIS|COMMENT|DX|DESCRIPTION|DESC|GROSS'
        self.bad_section = r'CLINICAL|Note'
        self.pre_negation = r'( not | no |previous|negative |free of | near|above|below| from |without|against |(hx|history) of | \
                        to rule out|preclud| insufficient|suboptimal).{,75}'