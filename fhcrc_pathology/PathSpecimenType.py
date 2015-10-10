#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings

class PathSpecimenType(OneFieldPerSpecimen):
    __version__='SpecimenType1.0'
    
    def __init__(self):
        self.specimen_field_name ='SpecimenFindType'
        self.overall_field_name='SpecimenType'
        self.specimen_table = global_strings.FINDING_TABLE
        self.overall_table = global_strings.PATHOLOGY_TABLE
        self.specimen_confidence = 0.7
        self.unlabled_specimen_confidence = 0.5  
        self.return_dictionary_list = []        
        

        ## reference lists & dictionaries ##
        self.file_name_string = 'procedures'
        self.dz_specific_list = []
        self.dz_specific_standardizations = {}
        self.general_list = []
        self.general_standardizations = {}

        ## relevant sections of the report ##
        self.good_section = 'DIAGNOSIS|Specimen|DX|SPECIMEN'
        self.bad_section = 'CLINICAL'

