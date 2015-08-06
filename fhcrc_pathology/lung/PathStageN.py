#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

'''
        written October 2014, updates:
    December 2014 - added table_name to return dictionary
'''
import PathStage

class PathStageN(PathStage):
    __version__='PathStageN1.0'
    
    def __init__(self):
        self.stage_name='PathStageN'
        self.regex='.*(pT[012345][abc]?).*'
