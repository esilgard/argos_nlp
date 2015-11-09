'''author@esilgard'''
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from SecondaryField import SecondaryField

class PathGrade(SecondaryField):
    ''' extract the pathological grade based on a specific histology '''
    __version__ = 'PathGrade1.0'

    def __init__(self):
        self.field_name = 'PathGrade'
        self.standardization_dictionary = {'high': 'high', 'low': 'low', 'intermediate': \
                                           'intermediate', '3': 'high', '1': 'low', '2': \
                                           'intermediate', 'iii': 'high', 'i': 'low', 'ii': \
                                           'intermediate', 'moderate': 'moderate', 'poor': 'poor',}

        self.pre_window = 30
        self.post_window = 30
        self.return_d = {}
        self.strings1 = r'(high|low|intermediate|1|2|3|4|i|ii|iii|iv)'
        self.strings2 = r'(who|fnclcc)'
        self.strings3 = r'(well|poor|moderate)'
        ## each tuple represents a match string and it's appropriate match group
        self.patterns = [(r'.*([\W]|^)(' + self.strings3 + r'.{,15}differentiat[ioned]+).*', 2), \
                         (r'.*(grade.{,15}[\W]' + self.strings1 + r')([\W]|$).*', 2), \
                         (r'.*([\W]|^)(' + self.strings1 + r'[\W].{,15}grade).*', 2), \
                         (r'.*([\W]|^)(([123])[/of ]{1,6}3.{,20}fnclcc).*', 2), \
                         (r'.*(fnclcc .{,20}([123])[/of ]{1,6}3)([\W]|$).*', 1), \
                         (r'.*([\W]|^)(' + self.strings2 + r'.{,20}grade.{,5}[\W]' + \
                          self.strings1 + r')([\W]|$).*', 2)]
