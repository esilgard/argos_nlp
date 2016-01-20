'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import re
import global_strings as gb

class OneFieldPerReport(object):
    '''
    extract the value of a field which has one unambiguous value
    per report from the pathology report
    '''
    __version__ = 'OneFieldPerReport1.0'

    def __init__(self):
        self.field_name = 'Default'
        self.regex = ''
        self.return_d = {}
        self.confidence = 0.0
        self.match_style = 'Default'
        self.table = 'Default'
        self.value_type = 'Default'

    def get_version(self):
        ''' return algorithm version'''
        return self.__version__

    def get(self, disease_group, dictionary):
        ''' find field match based on different match types (greedy, all, etc '''
        try:
            full_text = dictionary[(-1, 'FullText', 0, None)]
            self.return_d = {gb.NAME: self.field_name, gb.VALUE: None, gb.CONFIDENCE: 0.0, \
                             gb.KEY: gb.ALL, gb.VERSION: self.get_version(),\
                             gb.STARTSTOPS: [], gb.TABLE: self.table}
            ## match type object for equivilance test - this determines whether the value
            ## is based on the pattern match, or is a predetermined value
            sre_match_type = type(re.match("", ""))
            match = None
            ## handle different match types: greedy, non greedy, or multiple string match
            if self.match_style == 'first':
                match = re.match(r'.*?' + self.regex + '.*', full_text, re.DOTALL)
            elif self.match_style == 'last':
                match = re.match(r'.*' + self.regex + '.*', full_text, re.DOTALL)
            elif self.match_style == 'all':
                match = re.finditer(self.regex, full_text, re.DOTALL)
            if match:
                if (self.value_type) != dict:
                    self.return_d[gb.CONFIDENCE] = ('%.2f' % self.confidence)
                ## the field value will be based on the string match itself
                if isinstance(match, sre_match_type):
                    ## making the value into a datetime --
                    ## TODO this should be moved into a separate class to handle other date formats
                    if self.field_name == 'PathDate':
                        year = match.group(3)
                        month = match.group(1)
                        day = match.group(2)
                        if len(match.group(2)) == 1:
                            day = '0' + match.group(2)
                        self.return_d[gb.VALUE] = year + '-' + month + '-' + day
                        self.return_d[gb.STARTSTOPS].append\
                                    ({gb.START: match.start(1), gb.STOP: match.end(3)})
                    else:
                        if (self.value_type) != dict:
                            ## hacky string normalization for Pathologist
                            self.return_d[gb.VALUE] = match.group(1).replace('  ', ' ')
                        else:
                            self.return_d[gb.VALUE] = self.value_type.get(True)[0]
                            self.return_d[gb.CONFIDENCE] = ('%.2f' % self.value_type.get(True)[1])
                            self.return_d[gb.STARTSTOPS].append\
                                        ({gb.START: match.start(1), gb.STOP:match.end(1)})
                ## iterate through match iterator for 'all' style fields, which may have multiple
                else:
                    for each_match in match:
                        if not isinstance(self.value_type, dict):
                            ## hacky string normalization for PathStageSystem
                            self.return_d[gb.VALUE] = each_match.group(1).replace(',', '')
                        else:
                            self.return_d[gb.VALUE] = self.value_type.get(True)[0]
                            self.return_d[gb.CONFIDENCE] = ('%.2f' % self.value_type.get(True)[1])
                        self.return_d[gb.STARTSTOPS].append({gb.START:each_match.start(1), gb.STOP: each_match.end(1)})

            ## no match && value_type && dictionary -> value is based on lack of evidence (reviews)
            if isinstance(self.value_type, dict) and self.return_d[gb.VALUE] is None:
                self.return_d[gb.VALUE] = self.value_type.get(False)[0]
                self.return_d[gb.CONFIDENCE] = ('%.2f' % self.value_type.get(False)[1])
            return ([self.return_d], list)
        except RuntimeError:
            return ([{gb.ERR_TYPE: 'Warning', gb.ERR_STR: 'ERROR in %s module.' \
                      % self.field_name}], Exception)
