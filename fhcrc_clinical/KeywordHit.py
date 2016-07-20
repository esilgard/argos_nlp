#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import re
import os
import global_strings as gb
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class KeywordHit(object):
    '''
    search for relevant keywords and return positive hits with character offsets
    '''
    __version__ = 'KeywordHit1.0'
    def __init__(self):
        self.field_name = 'Default'
        self.regex = ''
        self.return_d = {}
        self.table = 'Default'
        self.value = 'Default'

    def get_version(self):
        ''' return algorithm version'''
        return self.__version__

    def get(self, dictionary):

        ''' find keyword matches based on relevant keyword list/regex '''
        try:
            full_text = dictionary[(-1, 'FullText', 0)]
            self.return_d = {gb.NAME: self.field_name, gb.VALUE: None, gb.CONFIDENCE: ('%.2f' % 0.0), \
                gb.KEY: gb.ALL, gb.VERSION: self.get_version(),\
                gb.STARTSTOPS: [], gb.TABLE: self.table}

            ## placeholder for some sort of match object or iterator ...whatever you need
            match = re.finditer(self.regex, full_text, re.DOTALL)
            if match:                
                for each_match in match:
                    self.return_d[gb.VALUE] = 'True'
                    self.return_d[gb.STARTSTOPS].append({gb.START:each_match.start(1), gb.STOP: each_match.end(1)})

            ## println to check on/debug char offsets
            #if self.return_d[gb.STARTSTOPS]:                
            #    print 'keyword hit in ', self.__version__ , ' at ', [(a['startPosition'],a['stopPosition']) for a in self.return_d[gb.STARTSTOPS]]
            return ([self.return_d], list)
        except RuntimeError:
            return ([{gb.ERR_TYPE: 'Warning', gb.ERR_STR: 'ERROR in %s module.' \
                 % self.field_name}], Exception)
