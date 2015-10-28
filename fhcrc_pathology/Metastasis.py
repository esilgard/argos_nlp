
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from SecondaryField import SecondaryField
import global_strings


class Metastasis(SecondaryField):
    __version__='Metastasis1.0'
    
    def __init__(self):        
        self.field_name = 'Metastasis'
        
        self.pre_window = 30
        self.post_window = 0
        self.return_dictionary={}
        self.strings1 = r'(metastasis|metastases|metastatic)'
        ## each tuple represents a match string and it's appropriate match group
        self.patterns = [(r'.*([\W]|^)('+self.strings1+r').*',2)]
       
