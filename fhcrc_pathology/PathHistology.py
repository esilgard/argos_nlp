# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings

class PathHistology(OneFieldPerSpecimen):
    __version__='PathHistology1.0'
    
    def __init__(self):
        self.specimen_field_name ='PathFindHistology'
        self.overall_field_name='PathHistology'
        self.specimen_table = global_strings.FINDING_TABLE
        self.overall_table = global_strings.PATHOLOGY_TABLE
        self.specimen_confidence = 0.9
        self.unlabled_specimen_confidence = 0.7
         
        self.return_dictionary_list = []        
        
        ## reference lists & dictionaries ##
        self.file_name_string = 'histologies'
        self.dz_specific_list = []
        self.dz_specific_standardizations = {}
        self.general_list = []
        self.general_standardizations = {}

        ## relevant sections of the report ##
        self.good_section = 'IMPRESSION|FINAL DIAGNOSIS|COMMENT|DX|SUMMARY CANCER'
        self.bad_section = 'CLINICAL'

        ## there is a secondary data element that should be searched for
        ## based on either position or value of the first e.g. PathGrade
        self.has_secondary_data_element = True
        self.secondary_data_elements = ['PathGrade','Metastasis']
