#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#


from KeywordHit import KeywordHit
import global_strings as gb

class AlcoholKeyword(KeywordHit):
    ''' find alcohol/drinking related keywords '''
    __version__ = 'AlcoholKeyword1.0'
    def __init__(self):
        super(AlcoholKeyword, self).__init__()
        self.field_name = 'AlcoholKeyword'
        ## parentheses make the match group capturable
        self.regex = r'([Aa]lcohol)'
        self.table = 'KeywordHitTable'
