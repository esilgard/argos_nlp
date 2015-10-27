#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OneFieldPerSpecimen import OneFieldPerSpecimen
import global_strings

class PathSide(OneFieldPerSpecimen):
    __version__='PathSide.0'
    
    def __init__(self):
        self.specimen_field_name ='PathFindSide'
        self.overall_field_name='PathSide'
        self.specimen_table = global_strings.FINDING_TABLE
        self.overall_table = global_strings.PATHOLOGY_TABLE
        self.specimen_confidence = 0.97
        self.unlabled_specimen_confidence = 0.9
        
  
        self.return_dictionary_list = []       
        

        ## reference lists & dictionaries ##
        self.file_name_string = 'sides'
        self.dz_specific_list = []
        self.dz_specific_standardizations = {}
        self.general_list = []
        self.general_standardizations = {}

        ## relevant sections of the report ##
        self.good_section = 'SPECIMEN|Specimen|DESCRIPTION|IMPRESSION|DIAGNOSIS'
        self.bad_section = 'CLINICAL'
       
        ## ability to infer new value from one or more existing ones
        self.inference_flag=True



    def infer(self,finding_set):       
        ## infer 'bilateral' if the finding set is specifically only 'right' and 'left'
        if finding_set==set(['Right','Left']):            
            finding_set=set(['Bilateral']
        return finding_set
