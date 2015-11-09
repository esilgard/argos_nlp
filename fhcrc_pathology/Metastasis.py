'''author@esilgard'''
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from SecondaryField import SecondaryField

class Metastasis(SecondaryField):
    '''
    find eveidence of metastisis relating to a specific histology
    '''
    __version__ = 'Metastasis1.0'
    def __init__(self):
        self.field_name = 'Metastasis'
        self.pre_window = 30
        self.post_window = 0
        self.return_d = {}
        self.strings1 = r'(metastasis|metastases|metastatic)'
        ## each tuple represents a match string and it's appropriate match group
        self.patterns = [(r'.*([\W]|^)(' + self.strings1 + r').*', 2)]
