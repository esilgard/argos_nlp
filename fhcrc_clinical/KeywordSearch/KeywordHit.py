#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import re
import os
from fhcrc_clinical.global_strings import *
from fhcrc_clinical.KeywordSearch.KeywordGlobals import *
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep


class KeywordHit(object):
    """search for relevant keywords and return positive hits with character offsets"""
    __version__ = 'KeywordHit1.0'

    def __init__(self):
        self.field_name = 'Default'
        self.regex = ''
        self.return_d = {}
        self.table = 'Default'
        self.value = 'Default'

    def get_version(self):
        """ return algorithm version"""
        return self.__version__

    def get(self, dictionary):
        """ find keyword matches based on relevant keyword list/regex """
        try:
            self.find_keyword_matches(dictionary)
            return [self.return_d], list
        except RuntimeError:
            return [{ERR_TYPE: 'Warning', ERR_STR: 'ERROR in %s module.' % self.field_name}], Exception

    @staticmethod
    def get_regex_from_file(substance):
        # get regexes
        filename = PATH + substance + KEYWORD_FILE_SUFFIX
        with open(filename, "r") as regex_file:
            regex_lines = regex_file.readlines()
            regexes = [r[:-1] for r in regex_lines]     # remove "\n" at end of each regex line

        # OR regexes together to get one big regex
        regex = r"((" + ")|(".join(regexes) + "))"
        return regex

    def find_keyword_matches(self, dictionary):
        full_text = dictionary[(-1, 'FullText', 0)]
        self.return_d = {NAME: self.field_name, VALUE: None, CONFIDENCE: ('%.2f' % 0.0),
                         KEY: ALL, VERSION: self.get_version(),
                         STARTSTOPS: [], TABLE: self.table}

        # placeholder for some sort of match object or iterator ...whatever you need
        matches = re.finditer(self.regex, full_text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            self.return_d[VALUE] = 'True'
            self.return_d[STARTSTOPS].append({START: match.start(1), STOP: match.end(1)})

        # println to check on/debug char offsets
        #if self.return_d[STARTSTOPS]:
        #    print 'keyword hit in ', self.__version__, ' at ', [(a['startPosition'], a['stopPosition']) for a in self.return_d[STARTSTOPS]]
