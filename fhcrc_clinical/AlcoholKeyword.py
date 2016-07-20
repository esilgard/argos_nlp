#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#


from fhcrc_clinical.KeywordSearch.KeywordHit import KeywordHit
from fhcrc_clinical.KeywordSearch.KeywordGlobals import *


class AlcoholKeyword(KeywordHit):
    """ find alcohol/drinking related keywords """
    __version__ = 'AlcoholKeyword1.0'

    def __init__(self):
        super(AlcoholKeyword, self).__init__()
        self.field_name = 'AlcoholKeyword'
        self.regex = KeywordHit.get_regex_from_file(ALCOHOL)
        self.table = 'KeywordHitTable'
