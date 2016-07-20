#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#


from KeywordHit import KeywordHit
import global_strings as gb

class TobaccoKeyword(KeywordHit):
    ''' find tobacco/smoking related keywords '''
    __version__ = 'TobaccoKeyword1.0'
    def __init__(self):
        super(TobaccoKeyword, self).__init__()
        self.field_name = 'TobaccoKeyword'
        ## parentheses make the match group capturable
        self.regex = r'(([Tt]obacco)|([sS]mok((e[sr]?)|(ing))))'
        self.table = 'KeywordHitTable'
