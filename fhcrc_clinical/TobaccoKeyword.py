#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from fhcrc_clinical.KeywordSearch.KeywordHit import KeywordHit
from fhcrc_clinical.KeywordSearch.KeywordGlobals import *
print 'importing tob keyword'


class TobaccoKeyword(KeywordHit):
    """ find tobacco/smoking related keywords """
    __version__ = 'TobaccoKeyword1.0'

    def __init__(self):
        super(TobaccoKeyword, self).__init__()
        self.field_name = 'TobaccoKeyword'
        self.regex = KeywordHit.get_regex_from_file(TOBACCO)
        self.table = 'KeywordHitTable'
