'''author@esilgard'''
#
# Copyright (c) 2015-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import re, os
import global_strings as gb
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class SecondaryField(object):
    '''
    extract the value of a field which is dependant on another value
    '''
    __version__ = 'SecondaryField1.0'

    def __init__(self):
        self.field_name = 'Default'
        standardization_dictionary = {}
        self.return_d = {}
        ## variable window sizes based on primary field string matches ##
        self.pre_window = 0
        self.post_window = 0

        self.strings1 = r''
        self.strings2 = r''
        self.patterns = []

    def get_version(self):
        ''' return algorithm version '''
        return self.__version__

    def get(self, primary_field_dictionary, text):
        ''' retrieve evidence of a data element based on the location/value of another element '''
        ## general sets to track and aggregate overall findings for the text
        finding_set = set([])
        start_stops_set = set([])
        ## a dictionary of offsets for each string match in primary field dictionary
        primary_offsets = primary_field_dictionary[gb.STARTSTOPS]

        ## loop through primary field matches
        for offsets in primary_offsets:
            ## loop through secondary patterns
            for pattern in self.patterns:
                ## find first match in each pattern in restricted window around primary value
                p = re.match(pattern[0], text[offsets[gb.START]-self.pre_window: \
                            offsets[gb.STOP]+self.post_window].lower(), re.DOTALL)
                if p:
                    finding_set.add(p.group(pattern[1]))
                    start_stops_set.add((p.start(pattern[1]) + (offsets[gb.START]-30), \
                                         p.end(pattern[1]) + (offsets[gb.START]-30)))

        if finding_set:
            self.return_d = {gb.NAME: self.field_name, \
                                      gb.KEY: primary_field_dictionary[gb.KEY], \
                                      gb.TABLE: primary_field_dictionary[gb.TABLE], \
                                      gb.VERSION: self.get_version(), \
                                      gb.VALUE: ';'.join(finding_set), \
                                      gb.CONFIDENCE: (primary_field_dictionary[gb.CONFIDENCE]), \
                                      gb.STARTSTOPS: [{gb.START: char[0], gb.STOP: char[1]} \
                                                      for char in start_stops_set]}

        return self.return_d
